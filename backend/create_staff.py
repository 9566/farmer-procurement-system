from database import SessionLocal
from models import StaffUser
from auth import hash_password


# ============================================================
# ADMIN DETAILS
# ============================================================

NAME = "Main Admin"

MOBILE = "9999999999"

PASSWORD = "Admin@123"

ROLE = "admin"

CENTRE_ID = None


# ============================================================
# CREATE ADMIN
# ============================================================

db = SessionLocal()

try:

    existing = (
        db.query(StaffUser)
        .filter(
            StaffUser.mobile == MOBILE
        )
        .first()
    )

    if existing:

        print("===================================")
        print("Staff user already exists.")
        print("===================================")

    else:

        staff = StaffUser(
            name=NAME,
            mobile=MOBILE,
            password=hash_password(
                PASSWORD
            ),
            role=ROLE,
            centre_id=CENTRE_ID
        )

        db.add(staff)
        db.commit()
        db.refresh(staff)

        print("===================================")
        print("ADMIN CREATED SUCCESSFULLY")
        print("===================================")
        print("Staff ID :", staff.staff_id)
        print("Name     :", NAME)
        print("Mobile   :", MOBILE)
        print("Role     :", ROLE)
        print("===================================")

finally:

    db.close()