"""
Admin and staff management.
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

from auth import (
    create_access_token,
    hash_password,
    require_role,
    verify_password,
)

from database import get_db


# ============================================================
# ROUTERS
# ============================================================

auth_router = APIRouter(
    tags=["Authentication"]
)


router = APIRouter(
    prefix="/admin",
    tags=["Admin"]
)


# ============================================================
# STAFF LOGIN
# ============================================================

@auth_router.post(
    "/auth/staff-login",
    response_model=schemas.Token
)
def staff_login(
    credentials: schemas.StaffLogin,
    db: Session = Depends(get_db)
):

    staff = db.query(
        models.StaffUser
    ).filter(
        models.StaffUser.mobile == credentials.mobile
    ).first()


    if not staff:

        raise HTTPException(
            status_code=401,
            detail="Invalid mobile number or password"
        )


    if not verify_password(
        credentials.password,
        staff.password
    ):

        raise HTTPException(
            status_code=401,
            detail="Invalid mobile number or password"
        )


    # --------------------------------------------------------
    # TOKEN
    # --------------------------------------------------------

    token = create_access_token(
        {
            "sub": str(staff.staff_id),

            "role": staff.role,

            "centre_id": staff.centre_id,
        }
    )


    return schemas.Token(

        access_token=token,

        token_type="bearer",

        role=staff.role,

        user_id=staff.staff_id,

        centre_id=staff.centre_id,
    )


# ============================================================
# STAFF ME
# ============================================================

@auth_router.get(
    "/auth/staff-me",
    response_model=schemas.StaffOut
)
def staff_me(
    payload: dict = Depends(
        require_role(
            "admin",
            "operator"
        )
    ),
    db: Session = Depends(get_db)
):

    staff = db.get(
        models.StaffUser,
        payload["user_id"]
    )


    if not staff:

        raise HTTPException(
            status_code=404,
            detail="Staff account not found"
        )


    return staff


# ============================================================
# ADMIN DASHBOARD
# ============================================================

@router.get(
    "/dashboard",
    response_model=schemas.DashboardStats
)
def dashboard(
    db: Session = Depends(get_db),
    payload: dict = Depends(
        require_role("admin")
    )
):

    total_farmers = db.query(
        func.count(
            models.Farmer.farmer_id
        )
    ).scalar() or 0


    today_bookings = db.query(
        func.count(
            models.Booking.booking_id
        )
    ).filter(
        models.Booking.booking_date == date.today()
    ).scalar() or 0


    active_centres = db.query(
        func.count(
            models.ProcurementCentre.centre_id
        )
    ).scalar() or 0


    waiting = db.query(
        func.count(
            models.Queue.queue_id
        )
    ).filter(
        models.Queue.status == "WAITING"
    ).scalar() or 0


    procured = db.query(
        func.coalesce(
            func.sum(
                models.Procurement.actual_quantity
            ),
            0
        )
    ).filter(
        models.Procurement.procurement_status
        == "COMPLETED"
    ).scalar() or 0


    payments = db.query(
        func.coalesce(
            func.sum(
                models.Payment.amount
            ),
            0
        )
    ).filter(
        models.Payment.payment_status
        == "PAYMENT_COMPLETED"
    ).scalar() or 0


    return {

        "total_farmers":
            int(total_farmers),

        "today_bookings":
            int(today_bookings),

        "active_centres":
            int(active_centres),

        "waiting_farmers":
            int(waiting),

        "total_procured_quantity":
            float(procured),

        "total_payments_completed":
            float(payments),
    }


# ============================================================
# CROP ANALYTICS
# ============================================================

@router.get(
    "/analytics/crop-wise",
    response_model=list[schemas.CropAnalytics]
)
def crop_wise(
    db: Session = Depends(get_db),
    payload: dict = Depends(
        require_role("admin")
    )
):

    rows = db.query(

        models.Crop.crop_id,

        models.Crop.crop_name,

        func.coalesce(
            func.sum(
                models.Procurement.actual_quantity
            ),
            0
        ).label(
            "total_quantity"
        ),

        func.count(
            models.Booking.booking_id
        ).label(
            "total_bookings"
        ),

    ).join(
        models.Booking,
        models.Booking.crop_id
        == models.Crop.crop_id
    ).outerjoin(
        models.Procurement,
        models.Procurement.booking_id
        == models.Booking.booking_id
    ).filter(

        (
            models.Procurement.procurement_status
            == "COMPLETED"
        )

        |

        models.Procurement.procurement_id.is_(None)

    ).group_by(

        models.Crop.crop_id,

        models.Crop.crop_name

    ).all()


    return [

        {

            "crop_id": row[0],

            "crop_name": row[1],

            "total_quantity":
                float(row[2] or 0),

            "total_bookings":
                int(row[3]),

        }

        for row in rows

    ]


# ============================================================
# ADD CENTRE
# ============================================================

@router.post(
    "/centres",
    response_model=schemas.CentreOut,
    status_code=201
)
def add_centre(
    data: schemas.CentreCreate,
    db: Session = Depends(get_db),
    payload: dict = Depends(
        require_role("admin")
    )
):

    centre = models.ProcurementCentre(
        **data.model_dump()
    )

    db.add(
        centre
    )

    db.commit()

    db.refresh(
        centre
    )

    return centre


# ============================================================
# ADD CROP
# ============================================================

@router.post(
    "/crops",
    response_model=schemas.CropOut,
    status_code=201
)
def add_crop(
    data: schemas.CropCreate,
    db: Session = Depends(get_db),
    payload: dict = Depends(
        require_role("admin")
    )
):

    crop = models.Crop(
        **data.model_dump()
    )

    db.add(
        crop
    )

    db.commit()

    db.refresh(
        crop
    )

    return crop


# ============================================================
# CREATE STAFF
# ============================================================

@router.post(
    "/staff",
    response_model=schemas.StaffOut,
    status_code=201
)
def create_staff(
    data: schemas.StaffCreate,
    db: Session = Depends(get_db),
    payload: dict = Depends(
        require_role("admin")
    )
):

    # --------------------------------------------------------
    # OPERATOR
    # --------------------------------------------------------

    if data.role == "operator":

        if data.centre_id is None:

            raise HTTPException(
                status_code=400,
                detail=(
                    "Operator must have "
                    "a centre_id"
                )
            )


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
    # ADMIN
    # --------------------------------------------------------

    elif data.role == "admin":

        if data.centre_id is not None:

            raise HTTPException(
                status_code=400,
                detail=(
                    "Admin should not be "
                    "assigned to a centre"
                )
            )


    # --------------------------------------------------------
    # MOBILE
    # --------------------------------------------------------

    existing = db.query(
        models.StaffUser
    ).filter(
        models.StaffUser.mobile == data.mobile
    ).first()


    if existing:

        raise HTTPException(
            status_code=400,
            detail="Mobile number already registered"
        )


    # --------------------------------------------------------
    # STAFF
    # --------------------------------------------------------

    staff = models.StaffUser(

        name=data.name,

        mobile=data.mobile,

        password=hash_password(
            data.password
        ),

        role=data.role,

        centre_id=data.centre_id,
    )


    db.add(
        staff
    )


    try:

        db.commit()

        db.refresh(
            staff
        )

    except IntegrityError:

        db.rollback()

        raise HTTPException(
            status_code=400,
            detail="Unable to create staff account"
        )


    return staff