"""
Queue management.

GET  /queue/{centre_id}
GET  /queue/{centre_id}/position
POST /queue/next
WS   /ws/queue/{centre_id}
"""

from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    WebSocket,
    WebSocketDisconnect,
)

from sqlalchemy.orm import Session

import models

from auth import (
    get_current_user,
    require_role,
)

from database import (
    SessionLocal,
    get_db,
)

from services.notification import (
    create_notification,
    send_sms,
)

from services.queue_manager import manager


router = APIRouter(
    tags=["Queue"]
)


# ============================================================
# QUEUE SNAPSHOT
# ============================================================

def queue_snapshot(
    db: Session,
    centre_id: int,
):
    """
    Return the current queue for a procurement centre.

    Only WAITING and CALLED entries are displayed.
    SERVED and CANCELLED entries are excluded.
    """

    entries = (
        db.query(models.Queue)
        .filter(
            models.Queue.centre_id == centre_id,
            models.Queue.status.in_(
                ["WAITING", "CALLED"]
            ),
        )
        .order_by(
            models.Queue.queue_position.asc(),
            models.Queue.queue_id.asc(),
        )
        .all()
    )

    current_token = None
    waiting = []

    for entry in entries:

        if entry.status == "CALLED":

            # First CALLED farmer becomes current token
            if current_token is None:
                current_token = entry.token_number

        elif entry.status == "WAITING":

            waiting.append(entry.token_number)

    return {
        "centre_id": centre_id,
        "current_token": current_token,
        "waiting": waiting,
        "total_waiting": len(waiting),
    }


# ============================================================
# OPERATOR CENTRE ACCESS
# ============================================================

def check_centre_access(
    centre_id: int,
    payload: dict,
):
    """
    Operators can access only their assigned centre.
    Admin can access every centre.
    """

    role = payload.get("role")

    if role == "admin":
        return

    if role != "operator":
        raise HTTPException(
            status_code=403,
            detail="Invalid staff role",
        )

    assigned_centre = payload.get("centre_id")

    if assigned_centre is None:
        raise HTTPException(
            status_code=403,
            detail="Operator is not assigned to a centre",
        )

    try:
        assigned_centre = int(assigned_centre)
    except (TypeError, ValueError):
        raise HTTPException(
            status_code=403,
            detail="Invalid operator centre assignment",
        )

    if assigned_centre != centre_id:
        raise HTTPException(
            status_code=403,
            detail="Operator is not assigned to this centre",
        )


# ============================================================
# PUBLIC QUEUE
# ============================================================

@router.get("/queue/{centre_id}")
def get_queue(
    centre_id: int,
    db: Session = Depends(get_db),
):
    """
    Get current queue for a centre.
    """

    centre = db.get(
        models.ProcurementCentre,
        centre_id,
    )

    if not centre:
        raise HTTPException(
            status_code=404,
            detail="Centre not found",
        )

    return queue_snapshot(
        db,
        centre_id,
    )


# ============================================================
# QUEUE POSITION
# ============================================================

@router.get("/queue/{centre_id}/position")
def get_position(
    centre_id: int,
    booking_id: int,
    db: Session = Depends(get_db),
    payload: dict = Depends(get_current_user),
):
    """
    Get queue position for a booking.
    """

    entry = (
        db.query(models.Queue)
        .filter(
            models.Queue.centre_id == centre_id,
            models.Queue.booking_id == booking_id,
        )
        .first()
    )

    if not entry:
        raise HTTPException(
            status_code=404,
            detail="Queue entry not found",
        )

    booking = db.get(
        models.Booking,
        booking_id,
    )

    if not booking:
        raise HTTPException(
            status_code=404,
            detail="Booking not found",
        )

    role = payload.get("role")

    # --------------------------------------------------------
    # FARMER
    # --------------------------------------------------------

    if role == "farmer":

        if booking.farmer_id != payload.get("user_id"):
            raise HTTPException(
                status_code=403,
                detail="You cannot access this queue position",
            )

    # --------------------------------------------------------
    # OPERATOR
    # --------------------------------------------------------

    elif role == "operator":

        check_centre_access(
            centre_id,
            payload,
        )

    # --------------------------------------------------------
    # ADMIN
    # --------------------------------------------------------

    elif role != "admin":

        raise HTTPException(
            status_code=403,
            detail="Invalid role",
        )

    return {
        "booking_id": booking_id,
        "queue_position": entry.queue_position,
        "status": entry.status,
        "token_number": entry.token_number,
    }


# ============================================================
# CALL NEXT FARMER
# ============================================================

@router.post("/queue/next")
async def call_next(
    centre_id: int,
    db: Session = Depends(get_db),
    payload: dict = Depends(
        require_role(
            "operator",
            "admin",
        )
    ),
):
    """
    Call the next WAITING farmer.
    """

    check_centre_access(
        centre_id,
        payload,
    )

    # --------------------------------------------------------
    # CHECK CENTRE
    # --------------------------------------------------------

    centre = db.get(
        models.ProcurementCentre,
        centre_id,
    )

    if not centre:
        raise HTTPException(
            status_code=404,
            detail="Centre not found",
        )

    # --------------------------------------------------------
    # LOCK CENTRE
    #
    # Prevent two operators from calling two farmers
    # simultaneously.
    # --------------------------------------------------------

    db.query(
        models.ProcurementCentre
    ).filter(
        models.ProcurementCentre.centre_id == centre_id
    ).with_for_update().first()

    # --------------------------------------------------------
    # CHECK CURRENT CALLED FARMER
    # --------------------------------------------------------

    current = (
        db.query(models.Queue)
        .filter(
            models.Queue.centre_id == centre_id,
            models.Queue.status == "CALLED",
        )
        .order_by(
            models.Queue.queue_position.asc()
        )
        .first()
    )

    if current:

        raise HTTPException(
            status_code=409,
            detail=(
                f"Token {current.token_number} "
                "is already being served"
            ),
        )

    # --------------------------------------------------------
    # FIND NEXT WAITING FARMER
    # --------------------------------------------------------

    entry = (
        db.query(models.Queue)
        .filter(
            models.Queue.centre_id == centre_id,
            models.Queue.status == "WAITING",
        )
        .order_by(
            models.Queue.queue_position.asc(),
            models.Queue.queue_id.asc(),
        )
        .with_for_update()
        .first()
    )

    if not entry:

        raise HTTPException(
            status_code=404,
            detail="No one waiting in this queue",
        )

    # --------------------------------------------------------
    # GET BOOKING
    # --------------------------------------------------------

    booking = db.get(
        models.Booking,
        entry.booking_id,
    )

    if not booking:

        entry.status = "CANCELLED"

        db.commit()

        raise HTTPException(
            status_code=404,
            detail="Booking associated with queue entry not found",
        )

    # --------------------------------------------------------
    # UPDATE QUEUE
    # --------------------------------------------------------

    entry.status = "CALLED"

    booking.status = "CALLED"

    # --------------------------------------------------------
    # NOTIFICATION
    # --------------------------------------------------------

    message = (
        f"Your token {entry.token_number} "
        "has been called. "
        "Please proceed to the procurement centre."
    )

    farmer_mobile = None

    if booking.farmer:
        farmer_mobile = booking.farmer.mobile

    notification = create_notification(
        db=db,
        farmer_id=booking.farmer_id,
        message=message,
        notification_type="TOKEN_CALLED",
    )

    # --------------------------------------------------------
    # COMMIT
    # --------------------------------------------------------

    try:

        db.commit()

    except Exception:

        db.rollback()
        raise

    # --------------------------------------------------------
    # SMS AFTER DATABASE COMMIT
    # --------------------------------------------------------

    if farmer_mobile:

        send_sms(
            farmer_mobile,
            message,
        )

    # --------------------------------------------------------
    # BROADCAST
    # --------------------------------------------------------

    snapshot = queue_snapshot(
        db,
        centre_id,
    )

    await manager.broadcast(
        centre_id,
        snapshot,
    )

    return snapshot


# ============================================================
# WEBSOCKET
# ============================================================

@router.websocket(
    "/ws/queue/{centre_id}"
)
async def queue_socket(
    websocket: WebSocket,
    centre_id: int,
):
    """
    Public read-only live queue display.

    Example:

    ws://localhost:8000/ws/queue/1
    """

    db = SessionLocal()

    try:

        # ----------------------------------------------------
        # CHECK CENTRE
        # ----------------------------------------------------

        centre = db.get(
            models.ProcurementCentre,
            centre_id,
        )

        if not centre:

            await websocket.close(
                code=1008,
                reason="Centre not found",
            )

            return

        # ----------------------------------------------------
        # CONNECT
        # ----------------------------------------------------

        await manager.connect(
            centre_id,
            websocket,
        )

        # ----------------------------------------------------
        # SEND INITIAL SNAPSHOT
        # ----------------------------------------------------

        await websocket.send_json(
            queue_snapshot(
                db,
                centre_id,
            )
        )

        # ----------------------------------------------------
        # KEEP CONNECTION ALIVE
        # ----------------------------------------------------

        while True:

            await websocket.receive_text()

            await websocket.send_json(
                queue_snapshot(
                    db,
                    centre_id,
                )
            )

    except WebSocketDisconnect:

        pass

    finally:

        manager.disconnect(
            centre_id,
            websocket,
        )

        db.close()