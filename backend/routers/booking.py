"""
Booking management.

Flow:

Farmer Login
     ↓
Create Booking
     ↓
Generate Token
     ↓
Create Queue Entry
     ↓
WAITING
"""

from datetime import date

from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
)

from sqlalchemy import func
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

import models
import schemas

from auth import get_current_user
from database import get_db

from services.notification import send_notification
from services.queue_manager import manager


router = APIRouter(
    prefix="/bookings",
    tags=["Booking"]
)


# ============================================================
# STAFF / FARMER ACCESS
# ============================================================

def check_booking_access(
    booking,
    payload: dict
):

    role = payload.get("role")

    if role == "farmer":

        if booking.farmer_id != payload.get(
            "user_id"
        ):

            raise HTTPException(
                status_code=403,
                detail="You cannot access this booking"
            )


    elif role == "operator":

        centre_id = payload.get(
            "centre_id"
        )

        if centre_id is None:

            raise HTTPException(
                status_code=403,
                detail="Operator is not assigned to a centre"
            )

        if int(centre_id) != booking.centre_id:

            raise HTTPException(
                status_code=403,
                detail="Operator is not assigned to this centre"
            )


    elif role != "admin":

        raise HTTPException(
            status_code=403,
            detail="Invalid role"
        )


# ============================================================
# CREATE BOOKING
# ============================================================

@router.post(
    "",
    response_model=schemas.BookingOut,
    status_code=201
)
async def create_booking(
    data: schemas.BookingCreate,
    db: Session = Depends(get_db),
    payload: dict = Depends(get_current_user)
):

    if payload.get("role") != "farmer":

        raise HTTPException(
            status_code=403,
            detail="Only farmers can create bookings"
        )


    farmer_id = payload["user_id"]


    # --------------------------------------------------------
    # FARMER
    # --------------------------------------------------------

    farmer = db.get(
        models.Farmer,
        farmer_id
    )

    if not farmer:

        raise HTTPException(
            status_code=401,
            detail="Farmer account not found"
        )


    # --------------------------------------------------------
    # DATE
    # --------------------------------------------------------

    if data.booking_date < date.today():

        raise HTTPException(
            status_code=400,
            detail="Booking date cannot be in the past"
        )


    # --------------------------------------------------------
    # CENTRE
    # --------------------------------------------------------

    centre = db.get(
        models.ProcurementCentre,
        data.centre_id
    )

    if not centre:

        raise HTTPException(
            status_code=404,
            detail="Procurement centre not found"
        )


    # --------------------------------------------------------
    # CROP
    # --------------------------------------------------------

    crop = db.get(
        models.Crop,
        data.crop_id
    )

    if not crop:

        raise HTTPException(
            status_code=404,
            detail="Crop not found"
        )


    # --------------------------------------------------------
    # DUPLICATE BOOKING
    # --------------------------------------------------------

    duplicate = db.query(
        models.Booking
    ).filter(
        models.Booking.farmer_id == farmer_id,
        models.Booking.centre_id == data.centre_id,
        models.Booking.booking_date == data.booking_date,
        models.Booking.slot == data.slot,
        models.Booking.status.notin_(
            [
                "CANCELLED",
                "PAYMENT_COMPLETED"
            ]
        )
    ).first()


    if duplicate:

        raise HTTPException(
            status_code=409,
            detail=(
                "You already have a booking "
                "for this centre, date and slot"
            )
        )


    # --------------------------------------------------------
    # DAILY CAPACITY
    # --------------------------------------------------------

    if centre.capacity_per_day:

        booking_count = db.query(
            func.count(
                models.Booking.booking_id
            )
        ).filter(
            models.Booking.centre_id == data.centre_id,
            models.Booking.booking_date == data.booking_date,
            models.Booking.status != "CANCELLED"
        ).scalar() or 0


        if booking_count >= centre.capacity_per_day:

            raise HTTPException(
                status_code=409,
                detail="Centre capacity is full for this date"
            )


    # --------------------------------------------------------
    # TOKEN
    # --------------------------------------------------------

    last_token = db.query(
        func.max(
            models.Booking.token_number
        )
    ).filter(
        models.Booking.centre_id == data.centre_id,
        models.Booking.booking_date == data.booking_date,
    ).scalar() or 0


    token_number = int(
        last_token
    ) + 1


    # --------------------------------------------------------
    # QUEUE POSITION
    # --------------------------------------------------------

    last_position = db.query(
        func.max(
            models.Queue.queue_position
        )
    ).filter(
        models.Queue.centre_id == data.centre_id,
        models.Queue.status != "CANCELLED"
    ).scalar() or 0


    queue_position = int(
        last_position
    ) + 1


    # --------------------------------------------------------
    # BOOKING
    # --------------------------------------------------------

    booking = models.Booking(

        farmer_id=farmer_id,

        centre_id=data.centre_id,

        crop_id=data.crop_id,

        quantity=data.quantity,

        booking_date=data.booking_date,

        slot=data.slot,

        token_number=token_number,

        status="BOOKED",
    )


    db.add(
        booking
    )


    try:

        db.flush()


        # ----------------------------------------------------
        # QUEUE
        # ----------------------------------------------------

        queue_entry = models.Queue(

            booking_id=booking.booking_id,

            centre_id=data.centre_id,

            token_number=token_number,

            queue_position=queue_position,

            status="WAITING",
        )


        db.add(
            queue_entry
        )


        # ----------------------------------------------------
        # NOTIFICATION
        # ----------------------------------------------------

        send_notification(

            db,

            farmer_id,

            (
                f"Booking confirmed successfully. "
                f"Your token number is {token_number}."
            ),

            "BOOKING_CONFIRMATION",
        )


        db.commit()

        db.refresh(
            booking
        )


    except IntegrityError:

        db.rollback()

        raise HTTPException(
            status_code=409,
            detail=(
                "Unable to create booking. "
                "Please try again."
            )
        )


    # --------------------------------------------------------
    # WEBSOCKET UPDATE
    # --------------------------------------------------------

    await manager.broadcast(
        data.centre_id,
        {
            "centre_id": data.centre_id,
            "message": "Queue updated"
        }
    )


    return booking


# ============================================================
# GET BOOKING
# ============================================================

@router.get(
    "/{booking_id}",
    response_model=schemas.BookingOut
)
def get_booking(
    booking_id: int,
    db: Session = Depends(get_db),
    payload: dict = Depends(get_current_user)
):

    booking = db.get(
        models.Booking,
        booking_id
    )

    if not booking:

        raise HTTPException(
            status_code=404,
            detail="Booking not found"
        )


    check_booking_access(
        booking,
        payload
    )

    return booking


# ============================================================
# CANCEL BOOKING
# ============================================================

@router.put(
    "/{booking_id}/cancel",
    response_model=schemas.BookingOut
)
async def cancel_booking(
    booking_id: int,
    db: Session = Depends(get_db),
    payload: dict = Depends(get_current_user)
):

    booking = db.get(
        models.Booking,
        booking_id
    )

    if not booking:

        raise HTTPException(
            status_code=404,
            detail="Booking not found"
        )


    check_booking_access(
        booking,
        payload
    )


    if booking.status in (
        "PAYMENT_COMPLETED",
        "PROCURED",
        "PAYMENT_PENDING"
    ):

        raise HTTPException(
            status_code=400,
            detail="This booking can no longer be cancelled"
        )


    booking.status = "CANCELLED"


    if booking.queue_entry:

        booking.queue_entry.status = "CANCELLED"


    db.commit()


    await manager.broadcast(
        booking.centre_id,
        {
            "centre_id": booking.centre_id,
            "message": "Queue updated"
        }
    )


    return booking