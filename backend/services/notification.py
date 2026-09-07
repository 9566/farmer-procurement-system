"""
Notification service.

Handles:
- Creating database notifications
- Sending SMS notifications
- Farmer notification retrieval
- Marking notifications as read
"""

import os
from pathlib import Path

from dotenv import load_dotenv
from sqlalchemy.orm import Session

import models


# ============================================================
# ENVIRONMENT
# ============================================================

BASE_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = BASE_DIR.parent.parent

load_dotenv(PROJECT_ROOT / ".env")


ENABLE_SMS = (
    os.getenv("ENABLE_SMS", "false")
    .strip()
    .lower()
    == "true"
)

TWILIO_ACCOUNT_SID = os.getenv("TWILIO_ACCOUNT_SID")
TWILIO_AUTH_TOKEN = os.getenv("TWILIO_AUTH_TOKEN")
TWILIO_PHONE_NUMBER = os.getenv("TWILIO_PHONE_NUMBER")


# ============================================================
# CREATE DATABASE NOTIFICATION
# ============================================================

def create_notification(
    db: Session,
    farmer_id: int,
    message: str,
    notification_type: str = "GENERAL"
):
    """
    Create a notification in the database.

    This function does NOT commit the transaction.
    The calling router is responsible for db.commit().
    """

    notification = models.Notification(
        farmer_id=farmer_id,
        message=message,
        notification_type=notification_type,
        is_read=False
    )

    db.add(notification)

    # Makes notification available immediately without
    # committing the entire transaction.
    db.flush()

    return notification


# ============================================================
# BACKWARD-COMPATIBILITY FUNCTION
# ============================================================

def send_notification(
    db: Session,
    farmer_id: int,
    message: str,
    notification_type: str = "GENERAL"
):
    """
    Backward-compatible wrapper.

    Older routers may still call send_notification().
    Internally it uses create_notification().
    """

    return create_notification(
        db=db,
        farmer_id=farmer_id,
        message=message,
        notification_type=notification_type
    )


# ============================================================
# NORMALIZE MOBILE NUMBER
# ============================================================

def normalize_mobile(mobile):
    """
    Convert Indian mobile numbers to +91XXXXXXXXXX format.
    """

    if not mobile:
        return None

    mobile = str(mobile).strip()

    # Already international format
    if mobile.startswith("+"):
        return mobile

    # Remove leading 0
    if len(mobile) == 11 and mobile.startswith("0"):
        mobile = mobile[1:]

    # Indian 10-digit number
    if len(mobile) == 10 and mobile.isdigit():
        return f"+91{mobile}"

    return None


# ============================================================
# SEND SMS
# ============================================================

def send_sms(
    mobile: str,
    message: str
):
    """
    Send SMS using Twilio.

    SMS is disabled by default unless ENABLE_SMS=true.
    """

    if not ENABLE_SMS:
        return False

    if not TWILIO_ACCOUNT_SID:
        print("SMS disabled: TWILIO_ACCOUNT_SID not configured")
        return False

    if not TWILIO_AUTH_TOKEN:
        print("SMS disabled: TWILIO_AUTH_TOKEN not configured")
        return False

    if not TWILIO_PHONE_NUMBER:
        print("SMS disabled: TWILIO_PHONE_NUMBER not configured")
        return False

    phone_number = normalize_mobile(mobile)

    if not phone_number:
        print("SMS failed: invalid mobile number")
        return False

    try:

        from twilio.rest import Client

        client = Client(
            TWILIO_ACCOUNT_SID,
            TWILIO_AUTH_TOKEN
        )

        client.messages.create(
            body=message,
            from_=TWILIO_PHONE_NUMBER,
            to=phone_number
        )

        return True

    except Exception as exc:

        # SMS failure should NOT break the database transaction.
        print(
            "SMS sending failed:",
            str(exc)
        )

        return False