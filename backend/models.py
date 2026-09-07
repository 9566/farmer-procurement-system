"""
SQLAlchemy models for Smart Farmer Procurement System.
"""

from sqlalchemy import (
    Boolean,
    Column,
    DECIMAL,
    Date,
    ForeignKey,
    Integer,
    String,
    Text,
    Time,
    TIMESTAMP,
    UniqueConstraint,
    func,
)

from sqlalchemy.orm import relationship

from database import Base


# ============================================================
# FARMER
# ============================================================

class Farmer(Base):

    __tablename__ = "farmers"

    farmer_id = Column(
        Integer,
        primary_key=True,
        index=True
    )

    name = Column(
        String(100),
        nullable=False
    )

    mobile = Column(
        String(15),
        unique=True,
        nullable=False,
        index=True
    )

    email = Column(
        String(100)
    )

    password = Column(
        String(255),
        nullable=False
    )

    address = Column(
        Text
    )

    village = Column(
        String(100)
    )

    district = Column(
        String(100)
    )

    state = Column(
        String(100)
    )

    created_at = Column(
        TIMESTAMP,
        server_default=func.now()
    )

    bookings = relationship(
        "Booking",
        back_populates="farmer"
    )

    notifications = relationship(
        "Notification",
        back_populates="farmer"
    )


# ============================================================
# PROCUREMENT CENTRE
# ============================================================

class ProcurementCentre(Base):

    __tablename__ = "procurement_centres"

    centre_id = Column(
        Integer,
        primary_key=True,
        index=True
    )

    centre_name = Column(
        String(150),
        nullable=False
    )

    location = Column(
        String(255)
    )

    district = Column(
        String(100)
    )

    capacity_per_day = Column(
        Integer
    )

    opening_time = Column(
        Time
    )

    closing_time = Column(
        Time
    )

    bookings = relationship(
        "Booking",
        back_populates="centre"
    )

    staff_users = relationship(
        "StaffUser",
        back_populates="centre"
    )


# ============================================================
# CROP
# ============================================================

class Crop(Base):

    __tablename__ = "crops"

    crop_id = Column(
        Integer,
        primary_key=True,
        index=True
    )

    crop_name = Column(
        String(100),
        nullable=False
    )

    minimum_support_price = Column(
        DECIMAL(10, 2)
    )

    unit = Column(
        String(20)
    )

    bookings = relationship(
        "Booking",
        back_populates="crop"
    )


# ============================================================
# BOOKING
# ============================================================

class Booking(Base):

    __tablename__ = "bookings"

    __table_args__ = (
        UniqueConstraint(
            "centre_id",
            "booking_date",
            "token_number",
            name="uq_booking_centre_date_token"
        ),
    )

    booking_id = Column(
        Integer,
        primary_key=True,
        index=True
    )

    farmer_id = Column(
        Integer,
        ForeignKey("farmers.farmer_id"),
        nullable=False
    )

    centre_id = Column(
        Integer,
        ForeignKey("procurement_centres.centre_id"),
        nullable=False
    )

    crop_id = Column(
        Integer,
        ForeignKey("crops.crop_id"),
        nullable=False
    )

    quantity = Column(
        DECIMAL(10, 2),
        nullable=False
    )

    booking_date = Column(
        Date,
        nullable=False
    )

    slot = Column(
        String(50),
        nullable=False
    )

    token_number = Column(
        Integer,
        nullable=False
    )

    status = Column(
        String(30),
        nullable=False,
        default="BOOKED"
    )

    farmer = relationship(
        "Farmer",
        back_populates="bookings"
    )

    centre = relationship(
        "ProcurementCentre",
        back_populates="bookings"
    )

    crop = relationship(
        "Crop",
        back_populates="bookings"
    )

    queue_entry = relationship(
        "Queue",
        back_populates="booking",
        uselist=False
    )

    procurement = relationship(
        "Procurement",
        back_populates="booking",
        uselist=False
    )

    payment = relationship(
        "Payment",
        back_populates="booking",
        uselist=False
    )


# ============================================================
# QUEUE
# ============================================================

class Queue(Base):

    __tablename__ = "queue"

    __table_args__ = (
        UniqueConstraint(
            "booking_id",
            name="uq_queue_booking"
        ),

        UniqueConstraint(
            "centre_id",
            "booking_id",
            name="uq_queue_centre_booking"
        ),
    )

    queue_id = Column(
        Integer,
        primary_key=True,
        index=True
    )

    booking_id = Column(
        Integer,
        ForeignKey("bookings.booking_id"),
        nullable=False
    )

    centre_id = Column(
        Integer,
        ForeignKey("procurement_centres.centre_id"),
        nullable=False
    )

    token_number = Column(
        Integer,
        nullable=False
    )

    queue_position = Column(
        Integer,
        nullable=False
    )

    status = Column(
        String(30),
        nullable=False,
        default="WAITING"
    )

    booking = relationship(
        "Booking",
        back_populates="queue_entry"
    )


# ============================================================
# PROCUREMENT
# ============================================================

class Procurement(Base):

    __tablename__ = "procurement"

    __table_args__ = (
        UniqueConstraint(
            "booking_id",
            name="uq_procurement_booking"
        ),
    )

    procurement_id = Column(
        Integer,
        primary_key=True,
        index=True
    )

    booking_id = Column(
        Integer,
        ForeignKey("bookings.booking_id"),
        nullable=False
    )

    actual_quantity = Column(
        DECIMAL(10, 2)
    )

    quality_status = Column(
        String(50)
    )

    procurement_date = Column(
        Date
    )

    procurement_status = Column(
        String(30),
        nullable=False,
        default="PENDING"
    )

    booking = relationship(
        "Booking",
        back_populates="procurement"
    )


# ============================================================
# PAYMENT
# ============================================================

class Payment(Base):

    __tablename__ = "payments"

    __table_args__ = (
        UniqueConstraint(
            "booking_id",
            name="uq_payment_booking"
        ),
    )

    payment_id = Column(
        Integer,
        primary_key=True,
        index=True
    )

    booking_id = Column(
        Integer,
        ForeignKey("bookings.booking_id"),
        nullable=False
    )

    farmer_id = Column(
        Integer,
        ForeignKey("farmers.farmer_id"),
        nullable=False
    )

    amount = Column(
        DECIMAL(10, 2),
        nullable=False,
        default=0
    )

    payment_method = Column(
        String(50)
    )

    transaction_id = Column(
        String(100)
    )

    payment_status = Column(
        String(30),
        nullable=False,
        default="PENDING"
    )

    payment_date = Column(
        TIMESTAMP,
        nullable=True
    )

    booking = relationship(
        "Booking",
        back_populates="payment"
    )


# ============================================================
# NOTIFICATION
# ============================================================

class Notification(Base):

    __tablename__ = "notifications"

    notification_id = Column(
        Integer,
        primary_key=True,
        index=True
    )

    farmer_id = Column(
        Integer,
        ForeignKey("farmers.farmer_id"),
        nullable=False
    )

    message = Column(
        Text,
        nullable=False
    )

    notification_type = Column(
        String(50)
    )

    is_read = Column(
        Boolean,
        nullable=False,
        default=False
    )

    created_at = Column(
        TIMESTAMP,
        server_default=func.now()
    )

    farmer = relationship(
        "Farmer",
        back_populates="notifications"
    )


# ============================================================
# STAFF USER
# ============================================================

class StaffUser(Base):

    __tablename__ = "staff_users"

    staff_id = Column(
        Integer,
        primary_key=True,
        index=True
    )

    name = Column(
        String(100),
        nullable=False
    )

    mobile = Column(
        String(15),
        unique=True,
        nullable=False,
        index=True
    )

    password = Column(
        String(255),
        nullable=False
    )

    role = Column(
        String(20),
        nullable=False
    )

    centre_id = Column(
        Integer,
        ForeignKey("procurement_centres.centre_id"),
        nullable=True
    )

    centre = relationship(
        "ProcurementCentre",
        back_populates="staff_users"
    )