from datetime import date
from decimal import Decimal, InvalidOperation

from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
)

from sqlalchemy.orm import Session

import models
import schemas

from database import get_db
from auth import require_role
from services.notification import send_notification


router = APIRouter(
    prefix="/procurement",
    tags=["Procurement"],
)


# =========================================================
# CREATE / UPDATE PROCUREMENT
# =========================================================

@router.post(
    "",
    response_model=schemas.ProcurementOut,
)
def create_or_update_procurement(
    booking_id: int,
    updates: schemas.ProcurementUpdate,
    db: Session = Depends(get_db),
    payload: dict = Depends(
        require_role(
            "operator",
            "admin",
        )
    ),
):
    # -----------------------------------------------------
    # FIND BOOKING
    # -----------------------------------------------------

    booking = (
        db.query(models.Booking)
        .filter(
            models.Booking.booking_id == booking_id
        )
        .first()
    )

    if not booking:
        raise HTTPException(
            status_code=404,
            detail="Booking not found",
        )

    # -----------------------------------------------------
    # OPERATOR CENTRE SECURITY
    # -----------------------------------------------------

    if payload.get("role") == "operator":

        operator_centre = payload.get("centre_id")

        if operator_centre is None:
            raise HTTPException(
                status_code=403,
                detail="Operator centre is not configured",
            )

        try:
            operator_centre = int(operator_centre)
        except (TypeError, ValueError):
            raise HTTPException(
                status_code=403,
                detail="Invalid operator centre",
            )

        if operator_centre != booking.centre_id:
            raise HTTPException(
                status_code=403,
                detail="Operator is not assigned to this centre",
            )

    # -----------------------------------------------------
    # VALIDATE ACTUAL QUANTITY
    # -----------------------------------------------------

    if updates.actual_quantity is not None:

        try:
            actual_quantity = Decimal(
                str(updates.actual_quantity)
            )
        except (InvalidOperation, ValueError, TypeError):

            raise HTTPException(
                status_code=400,
                detail="Invalid actual quantity",
            )

        if actual_quantity < 0:

            raise HTTPException(
                status_code=400,
                detail="Actual quantity cannot be negative",
            )

    # -----------------------------------------------------
    # FIND EXISTING PROCUREMENT
    # -----------------------------------------------------

    procurement = (
        db.query(models.Procurement)
        .filter(
            models.Procurement.booking_id == booking_id
        )
        .first()
    )

    # -----------------------------------------------------
    # CREATE PROCUREMENT IF NOT EXISTS
    # -----------------------------------------------------

    if not procurement:

        procurement = models.Procurement(
            booking_id=booking_id,
            procurement_date=date.today(),
            procurement_status="PENDING",
        )

        db.add(procurement)

        # Flush so SQLAlchemy knows the object exists
        # before further database operations.
        db.flush()

    # -----------------------------------------------------
    # UPDATE ACTUAL QUANTITY
    # -----------------------------------------------------

    if updates.actual_quantity is not None:

        procurement.actual_quantity = Decimal(
            str(updates.actual_quantity)
        )

    # -----------------------------------------------------
    # UPDATE QUALITY STATUS
    # -----------------------------------------------------

    if updates.quality_status is not None:

        procurement.quality_status = (
            updates.quality_status
        )

    # -----------------------------------------------------
    # UPDATE PROCUREMENT STATUS
    # -----------------------------------------------------

    if updates.procurement_status is not None:

        procurement.procurement_status = (
            updates.procurement_status
        )

    # -----------------------------------------------------
    # UPDATE PROCUREMENT DATE
    # -----------------------------------------------------

    procurement.procurement_date = date.today()

    # -----------------------------------------------------
    # WHEN PROCUREMENT IS COMPLETED
    # -----------------------------------------------------

    if procurement.procurement_status == "COMPLETED":

        # -------------------------------------------------
        # ACTUAL QUANTITY REQUIRED
        # -------------------------------------------------

        if procurement.actual_quantity is None:

            raise HTTPException(
                status_code=400,
                detail=(
                    "Actual quantity is required "
                    "before completing procurement"
                ),
            )

        # -------------------------------------------------
        # FIND CROP
        # -------------------------------------------------

        crop = (
            db.query(models.Crop)
            .filter(
                models.Crop.crop_id == booking.crop_id
            )
            .first()
        )

        if not crop:

            raise HTTPException(
                status_code=404,
                detail="Crop not found",
            )

        # -------------------------------------------------
        # CHECK MSP
        # -------------------------------------------------

        if crop.minimum_support_price is None:

            raise HTTPException(
                status_code=400,
                detail=(
                    "MSP is not configured "
                    "for this crop"
                ),
            )

        # -------------------------------------------------
        # PAYMENT CALCULATION
        # -------------------------------------------------

        actual_quantity = Decimal(
            str(procurement.actual_quantity)
        )

        msp = Decimal(
            str(crop.minimum_support_price)
        )

        payment_amount = (
            actual_quantity * msp
        )

        # -------------------------------------------------
        # FIND EXISTING PAYMENT
        # -------------------------------------------------

        payment = (
            db.query(models.Payment)
            .filter(
                models.Payment.booking_id == booking_id
            )
            .first()
        )

        # -------------------------------------------------
        # CREATE PAYMENT
        # -------------------------------------------------

        if not payment:

            payment = models.Payment(
                booking_id=booking_id,
                farmer_id=booking.farmer_id,
                amount=payment_amount,
                payment_status="PENDING",
            )

            db.add(payment)

        # -------------------------------------------------
        # UPDATE PAYMENT
        # -------------------------------------------------

        else:

            payment.amount = payment_amount

            # Don't reset a completed payment.
            if payment.payment_status != "PAYMENT_COMPLETED":

                payment.payment_status = "PENDING"

        # -------------------------------------------------
        # UPDATE BOOKING STATUS
        # -------------------------------------------------

        booking.status = "PAYMENT_PENDING"

        # -------------------------------------------------
        # SEND NOTIFICATION
        # -------------------------------------------------

        send_notification(
            db=db,
            farmer_id=booking.farmer_id,
            message=(
                "Procurement completed successfully. "
                f"Actual quantity: "
                f"{actual_quantity} "
                f"{crop.unit or ''}. "
                f"MSP: ₹{msp}. "
                f"Calculated payment: "
                f"₹{payment_amount:.2f}"
            ),
            notification_type="PROCUREMENT_COMPLETED",
        )

    # -----------------------------------------------------
    # PROCUREMENT NOT COMPLETED
    # -----------------------------------------------------

    else:

        booking.status = (
            procurement.procurement_status
            or "PENDING"
        )

    # -----------------------------------------------------
    # SAVE DATABASE
    # -----------------------------------------------------

    try:

        db.commit()

    except Exception:

        db.rollback()

        raise HTTPException(
            status_code=500,
            detail="Failed to save procurement",
        )

    # -----------------------------------------------------
    # REFRESH OBJECT
    # -----------------------------------------------------

    db.refresh(procurement)

    return procurement


# =========================================================
# GET PROCUREMENT
# =========================================================

@router.get(
    "/{booking_id}",
    response_model=schemas.ProcurementOut,
)
def get_procurement(
    booking_id: int,
    db: Session = Depends(get_db),
    payload: dict = Depends(
        require_role(
            "farmer",
            "operator",
            "admin",
        )
    ),
):

    # -----------------------------------------------------
    # FIND PROCUREMENT
    # -----------------------------------------------------

    procurement = (
        db.query(models.Procurement)
        .filter(
            models.Procurement.booking_id == booking_id
        )
        .first()
    )

    if not procurement:

        raise HTTPException(
            status_code=404,
            detail="No procurement record found",
        )

    # -----------------------------------------------------
    # FIND BOOKING
    # -----------------------------------------------------

    booking = (
        db.query(models.Booking)
        .filter(
            models.Booking.booking_id == booking_id
        )
        .first()
    )

    if not booking:

        raise HTTPException(
            status_code=404,
            detail="Booking not found",
        )

    # -----------------------------------------------------
    # FARMER SECURITY
    # -----------------------------------------------------

    if payload.get("role") == "farmer":

        user_id = payload.get("user_id")

        if user_id is None:

            raise HTTPException(
                status_code=401,
                detail="Invalid authentication payload",
            )

        try:
            user_id = int(user_id)

        except (TypeError, ValueError):

            raise HTTPException(
                status_code=401,
                detail="Invalid user ID",
            )

        if booking.farmer_id != user_id:

            raise HTTPException(
                status_code=403,
                detail="You cannot access this procurement",
            )

    # -----------------------------------------------------
    # OPERATOR CENTRE SECURITY
    # -----------------------------------------------------

    if payload.get("role") == "operator":

        operator_centre = payload.get("centre_id")

        if operator_centre is None:

            raise HTTPException(
                status_code=403,
                detail="Operator centre is not configured",
            )

        try:
            operator_centre = int(operator_centre)

        except (TypeError, ValueError):

            raise HTTPException(
                status_code=403,
                detail="Invalid operator centre",
            )

        if operator_centre != booking.centre_id:

            raise HTTPException(
                status_code=403,
                detail="Operator is not assigned to this centre",
            )

    # -----------------------------------------------------
    # RETURN PROCUREMENT
    # -----------------------------------------------------

    return procurement