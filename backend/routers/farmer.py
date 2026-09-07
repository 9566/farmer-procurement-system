"""
Farmer authentication, profile, centres, crops and notifications.
"""

from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    status,
)

from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

import models
import schemas

from auth import (
    create_access_token,
    get_current_user,
    hash_password,
    verify_password,
)

from database import get_db


router = APIRouter(
    tags=["Farmer"]
)


# ============================================================
# AUTHORIZATION HELPER
# ============================================================

def check_farmer_access(
    farmer_id: int,
    payload: dict
):

    role = payload.get("role")

    if role == "farmer":

        if payload.get("user_id") != farmer_id:

            raise HTTPException(
                status_code=403,
                detail="You cannot access another farmer's data"
            )

    elif role not in (
        "admin",
        "operator",
    ):

        raise HTTPException(
            status_code=403,
            detail="Invalid role"
        )


# ============================================================
# FARMER REGISTER
# ============================================================

@router.post(
    "/auth/register",
    response_model=schemas.FarmerOut,
    status_code=201
)
def register_farmer(
    data: schemas.FarmerRegister,
    db: Session = Depends(get_db)
):

    existing = db.query(
        models.Farmer
    ).filter(
        models.Farmer.mobile == data.mobile
    ).first()

    if existing:

        raise HTTPException(
            status_code=400,
            detail="Mobile number already registered"
        )


    farmer = models.Farmer(
        name=data.name,
        mobile=data.mobile,
        email=(
            str(data.email)
            if data.email
            else None
        ),
        password=hash_password(
            data.password
        ),
        address=data.address,
        village=data.village,
        district=data.district,
        state=data.state,
    )

    db.add(farmer)

    try:

        db.commit()

        db.refresh(farmer)

    except IntegrityError:

        db.rollback()

        raise HTTPException(
            status_code=400,
            detail="Mobile number already registered"
        )

    return farmer


# ============================================================
# FARMER LOGIN
# ============================================================

@router.post(
    "/auth/login",
    response_model=schemas.Token
)
def login_farmer(
    credentials: schemas.FarmerLogin,
    db: Session = Depends(get_db)
):

    farmer = db.query(
        models.Farmer
    ).filter(
        models.Farmer.mobile == credentials.mobile
    ).first()


    if not farmer:

        raise HTTPException(
            status_code=401,
            detail="Invalid mobile number or password"
        )


    if not verify_password(
        credentials.password,
        farmer.password
    ):

        raise HTTPException(
            status_code=401,
            detail="Invalid mobile number or password"
        )


    token = create_access_token(
        {
            "sub": str(farmer.farmer_id),
            "role": "farmer",
        }
    )


    return schemas.Token(
        access_token=token,
        role="farmer",
        user_id=farmer.farmer_id,
        centre_id=None,
    )


# ============================================================
# GET FARMER
# ============================================================

@router.get(
    "/farmers/{farmer_id}",
    response_model=schemas.FarmerOut
)
def get_farmer(
    farmer_id: int,
    db: Session = Depends(get_db),
    payload: dict = Depends(get_current_user)
):

    check_farmer_access(
        farmer_id,
        payload
    )

    farmer = db.get(
        models.Farmer,
        farmer_id
    )

    if not farmer:

        raise HTTPException(
            status_code=404,
            detail="Farmer not found"
        )

    return farmer


# ============================================================
# UPDATE FARMER
# ============================================================

@router.put(
    "/farmers/{farmer_id}",
    response_model=schemas.FarmerOut
)
def update_farmer(
    farmer_id: int,
    updates: schemas.FarmerUpdate,
    db: Session = Depends(get_db),
    payload: dict = Depends(get_current_user)
):

    check_farmer_access(
        farmer_id,
        payload
    )

    farmer = db.get(
        models.Farmer,
        farmer_id
    )

    if not farmer:

        raise HTTPException(
            status_code=404,
            detail="Farmer not found"
        )


    values = updates.model_dump(
        exclude_unset=True
    )


    for field, value in values.items():

        if field == "email" and value is not None:

            value = str(value)

        setattr(
            farmer,
            field,
            value
        )


    try:

        db.commit()

        db.refresh(farmer)

    except IntegrityError:

        db.rollback()

        raise HTTPException(
            status_code=400,
            detail="Unable to update farmer profile"
        )

    return farmer


# ============================================================
# FARMER BOOKINGS
# ============================================================

@router.get(
    "/farmers/{farmer_id}/bookings",
    response_model=list[schemas.BookingOut]
)
def get_farmer_bookings(
    farmer_id: int,
    db: Session = Depends(get_db),
    payload: dict = Depends(get_current_user)
):

    check_farmer_access(
        farmer_id,
        payload
    )

    if not db.get(
        models.Farmer,
        farmer_id
    ):

        raise HTTPException(
            status_code=404,
            detail="Farmer not found"
        )


    return db.query(
        models.Booking
    ).filter(
        models.Booking.farmer_id == farmer_id
    ).order_by(
        models.Booking.booking_date.desc(),
        models.Booking.booking_id.desc()
    ).all()


# ============================================================
# CENTRES
# ============================================================

@router.get(
    "/centres",
    response_model=list[schemas.CentreOut]
)
def list_centres(
    db: Session = Depends(get_db)
):

    return db.query(
        models.ProcurementCentre
    ).order_by(
        models.ProcurementCentre.centre_id
    ).all()


# ============================================================
# SINGLE CENTRE
# ============================================================

@router.get(
    "/centres/{centre_id}",
    response_model=schemas.CentreOut
)
def get_centre(
    centre_id: int,
    db: Session = Depends(get_db)
):

    centre = db.get(
        models.ProcurementCentre,
        centre_id
    )

    if not centre:

        raise HTTPException(
            status_code=404,
            detail="Centre not found"
        )

    return centre


# ============================================================
# CROPS
# ============================================================

@router.get(
    "/crops",
    response_model=list[schemas.CropOut]
)
def list_crops(
    db: Session = Depends(get_db)
):

    return db.query(
        models.Crop
    ).order_by(
        models.Crop.crop_id
    ).all()


# ============================================================
# NOTIFICATIONS
# ============================================================

@router.get(
    "/farmers/{farmer_id}/notifications",
    response_model=list[schemas.NotificationOut]
)
def get_notifications(
    farmer_id: int,
    db: Session = Depends(get_db),
    payload: dict = Depends(get_current_user)
):

    check_farmer_access(
        farmer_id,
        payload
    )

    return db.query(
        models.Notification
    ).filter(
        models.Notification.farmer_id == farmer_id
    ).order_by(
        models.Notification.created_at.desc()
    ).all()