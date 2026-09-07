"""
Pydantic v2 schemas.
"""

from datetime import date, datetime, time
from typing import Optional

from pydantic import (
    BaseModel,
    ConfigDict,
    EmailStr,
    Field,
)


# ============================================================
# FARMER
# ============================================================

class FarmerRegister(BaseModel):

    name: str = Field(
        min_length=2,
        max_length=100
    )

    mobile: str = Field(
        min_length=10,
        max_length=15
    )

    email: Optional[EmailStr] = None

    password: str = Field(
        min_length=6
    )

    address: Optional[str] = None

    village: Optional[str] = None

    district: Optional[str] = None

    state: Optional[str] = None


class FarmerLogin(BaseModel):

    mobile: str

    password: str


class FarmerOut(BaseModel):

    model_config = ConfigDict(
        from_attributes=True
    )

    farmer_id: int

    name: str

    mobile: str

    email: Optional[EmailStr] = None

    address: Optional[str] = None

    village: Optional[str] = None

    district: Optional[str] = None

    state: Optional[str] = None

    created_at: Optional[datetime] = None


class FarmerUpdate(BaseModel):

    name: Optional[str] = Field(
        default=None,
        min_length=2,
        max_length=100
    )

    email: Optional[EmailStr] = None

    address: Optional[str] = None

    village: Optional[str] = None

    district: Optional[str] = None

    state: Optional[str] = None


# ============================================================
# STAFF
# ============================================================

class StaffLogin(BaseModel):

    mobile: str

    password: str


class StaffCreate(BaseModel):

    name: str = Field(
        min_length=2,
        max_length=100
    )

    mobile: str = Field(
        min_length=10,
        max_length=15
    )

    password: str = Field(
        min_length=6
    )

    role: str = Field(
        pattern=r"^(admin|operator)$"
    )

    centre_id: Optional[int] = None


class StaffOut(BaseModel):

    model_config = ConfigDict(
        from_attributes=True
    )

    staff_id: int

    name: str

    mobile: str

    role: str

    centre_id: Optional[int] = None


# ============================================================
# CENTRE
# ============================================================

class CentreCreate(BaseModel):

    centre_name: str = Field(
        min_length=2,
        max_length=150
    )

    location: Optional[str] = None

    district: Optional[str] = None

    capacity_per_day: Optional[int] = Field(
        default=None,
        ge=0
    )

    opening_time: Optional[time] = None

    closing_time: Optional[time] = None


class CentreOut(CentreCreate):

    model_config = ConfigDict(
        from_attributes=True
    )

    centre_id: int


# ============================================================
# CROP
# ============================================================

class CropCreate(BaseModel):

    crop_name: str = Field(
        min_length=2,
        max_length=100
    )

    minimum_support_price: Optional[float] = Field(
        default=None,
        ge=0
    )

    unit: Optional[str] = Field(
        default=None,
        max_length=20
    )


class CropOut(CropCreate):

    model_config = ConfigDict(
        from_attributes=True
    )

    crop_id: int


# ============================================================
# BOOKING
# ============================================================

class BookingCreate(BaseModel):

    centre_id: int

    crop_id: int

    quantity: float = Field(
        gt=0
    )

    booking_date: date

    slot: str = Field(
        min_length=1,
        max_length=50
    )


class BookingOut(BaseModel):

    model_config = ConfigDict(
        from_attributes=True
    )

    booking_id: int

    farmer_id: int

    centre_id: int

    crop_id: int

    quantity: float

    booking_date: date

    slot: str

    token_number: int

    status: str


# ============================================================
# QUEUE
# ============================================================

class QueueOut(BaseModel):

    model_config = ConfigDict(
        from_attributes=True
    )

    queue_id: int

    booking_id: int

    centre_id: int

    token_number: int

    queue_position: int

    status: str


# ============================================================
# PROCUREMENT
# ============================================================

class ProcurementUpdate(BaseModel):

    actual_quantity: Optional[float] = Field(
        default=None,
        ge=0
    )

    quality_status: Optional[str] = Field(
        default=None,
        pattern=r"^(GOOD|AVERAGE|REJECTED)$"
    )

    procurement_status: Optional[str] = Field(
        default=None,
        pattern=r"^(PENDING|VERIFICATION|WEIGHING|COMPLETED)$"
    )


class ProcurementOut(BaseModel):

    model_config = ConfigDict(
        from_attributes=True
    )

    procurement_id: int

    booking_id: int

    actual_quantity: Optional[float] = None

    quality_status: Optional[str] = None

    procurement_date: Optional[date] = None

    procurement_status: str


# ============================================================
# PAYMENT
# ============================================================

class PaymentUpdate(BaseModel):

    payment_method: Optional[str] = Field(
        default=None,
        max_length=50
    )

    transaction_id: Optional[str] = Field(
        default=None,
        max_length=100
    )


class PaymentOut(BaseModel):

    model_config = ConfigDict(
        from_attributes=True
    )

    payment_id: int

    booking_id: int

    farmer_id: int

    amount: float

    payment_method: Optional[str] = None

    transaction_id: Optional[str] = None

    payment_status: str

    payment_date: Optional[datetime] = None


# ============================================================
# NOTIFICATION
# ============================================================

class NotificationOut(BaseModel):

    model_config = ConfigDict(
        from_attributes=True
    )

    notification_id: int

    farmer_id: int

    message: str

    notification_type: Optional[str] = None

    is_read: bool

    created_at: Optional[datetime] = None


# ============================================================
# TOKEN
# ============================================================

class Token(BaseModel):

    access_token: str

    token_type: str = "bearer"

    role: str

    user_id: int

    centre_id: Optional[int] = None


# ============================================================
# DASHBOARD
# ============================================================

class DashboardStats(BaseModel):

    total_farmers: int

    today_bookings: int

    active_centres: int

    waiting_farmers: int

    total_procured_quantity: float

    total_payments_completed: float


# ============================================================
# CROP ANALYTICS
# ============================================================

class CropAnalytics(BaseModel):

    crop_id: int

    crop_name: str

    total_quantity: float

    total_bookings: int