"""
Payment management.

IMPORTANT:

The frontend cannot control the payment amount.

Amount is always:

Actual Quantity × MSP
"""

from datetime import datetime, timezone

from decimal import Decimal

from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
)

from sqlalchemy.orm import Session

import models
import schemas

from auth import (
    get_current_user,
    require_role,
)

from database import get_db

from services.notification import send_notification


router = APIRouter(
    prefix="/payments",
    tags=["Payment"]
)


# ============================================================
# OPERATOR CENTRE CHECK
# ============================================================

def check_operator_centre(
    payload: dict,
    booking
):

    if payload.get("role") == "operator":

        centre_id = payload.get(
            "centre_id"
        )


        if centre_id is None:

            raise HTTPException(
                status_code=403,
                detail=(
                    "Operator is not assigned "
                    "to a centre"
                )
            )


        if int(centre_id) != booking.centre_id:

            raise HTTPException(
                status_code=403,
                detail=(
                    "Operator is not assigned "
                    "to this centre"
                )
            )


# ============================================================
# GET PAYMENT
# ============================================================

@router.get(
    "/{booking_id}",
    response_model=schemas.PaymentOut
)
def get_payment(
    booking_id: int,
    db: Session = Depends(get_db),
    payload: dict = Depends(
        require_role(
            "farmer",
            "operator",
            "admin"
        )
    )
):

    payment = db.query(
        models.Payment
    ).filter(
        models.Payment.booking_id == booking_id
    ).first()


    if not payment:

        raise HTTPException(
            status_code=404,
            detail="Payment not found"
        )


    booking = db.get(
        models.Booking,
        booking_id
    )


    if not booking:

        raise HTTPException(
            status_code=404,
            detail="Booking not found"
        )


    if payload["role"] == "farmer":

        if booking.farmer_id != payload["user_id"]:

            raise HTTPException(
                status_code=403,
                detail=(
                    "You cannot access "
                    "this payment"
                )
            )


    elif payload["role"] == "operator":

        check_operator_centre(
            payload,
            booking
        )


    return payment


# ============================================================
# COMPLETE PAYMENT
# ============================================================

@router.post(
    "/{booking_id}/complete",
    response_model=schemas.PaymentOut
)
def complete_payment(
    booking_id: int,
    updates: schemas.PaymentUpdate,
    db: Session = Depends(get_db),
    payload: dict = Depends(
        require_role(
            "admin",
            "operator"
        )
    )
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


    check_operator_centre(
        payload,
        booking
    )


    # --------------------------------------------------------
    # PROCUREMENT
    # --------------------------------------------------------

    procurement = db.query(
        models.Procurement
    ).filter(
        models.Procurement.booking_id == booking_id
    ).first()


    if not procurement:

        raise HTTPException(
            status_code=400,
            detail=(
                "Procurement record does not exist"
            )
        )


    if procurement.procurement_status != "COMPLETED":

        raise HTTPException(
            status_code=400,
            detail=(
                "Procurement must be completed "
                "before payment"
            )
        )


    if procurement.actual_quantity is None:

        raise HTTPException(
            status_code=400,
            detail="Actual quantity is missing"
        )


    # --------------------------------------------------------
    # CROP
    # --------------------------------------------------------

    crop = db.get(
        models.Crop,
        booking.crop_id
    )


    if not crop:

        raise HTTPException(
            status_code=404,
            detail="Crop not found"
        )


    if crop.minimum_support_price is None:

        raise HTTPException(
            status_code=400,
            detail=(
                "Crop MSP is not configured"
            )
        )


    # --------------------------------------------------------
    # PAYMENT
    # --------------------------------------------------------

    payment = db.query(
        models.Payment
    ).filter(
        models.Payment.booking_id == booking_id
    ).first()


    if not payment:

        payment = models.Payment(

            booking_id=booking_id,

            farmer_id=booking.farmer_id,

            amount=0,

            payment_status="PENDING",
        )

        db.add(
            payment
        )


    # --------------------------------------------------------
    # CALCULATE PAYMENT
    # --------------------------------------------------------

    amount = (

        Decimal(
            str(procurement.actual_quantity)
        )

        *

        Decimal(
            str(crop.minimum_support_price)
        )
    )


    payment.amount = amount


    # --------------------------------------------------------
    # UPDATE PAYMENT DETAILS
    # --------------------------------------------------------

    if updates.payment_method is not None:

        payment.payment_method = (
            updates.payment_method
        )


    if updates.transaction_id is not None:

        payment.transaction_id = (
            updates.transaction_id
        )


    # --------------------------------------------------------
    # PREVENT DUPLICATE PAYMENT
    # --------------------------------------------------------

    if payment.payment_status == "PAYMENT_COMPLETED":

        raise HTTPException(
            status_code=409,
            detail="Payment is already completed"
        )


    # --------------------------------------------------------
    # COMPLETE
    # --------------------------------------------------------

    payment.payment_status = (
        "PAYMENT_COMPLETED"
    )


    payment.payment_date = (
        datetime.now(timezone.utc)
    )


    booking.status = (
        "PAYMENT_COMPLETED"
    )


    # --------------------------------------------------------
    # NOTIFICATION
    # --------------------------------------------------------

    send_notification(

        db,

        booking.farmer_id,

        (
            "Payment completed successfully. "
            f"Amount: ₹{amount:.2f}. "
            f"Transaction ID: "
            f"{payment.transaction_id or 'N/A'}"
        ),

        "PAYMENT_COMPLETED",
    )


    # --------------------------------------------------------
    # COMMIT
    # --------------------------------------------------------

    db.commit()

    db.refresh(
        payment
    )


    return payment