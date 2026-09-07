import getpass

from database import SessionLocal
from models import StaffUser
from auth import hash_password


name = input("Admin name: ").strip()
mobile = input("Admin mobile: ").strip()
password = getpass.getpass("Admin password: ")


if not name:
    raise ValueError("Admin name cannot be empty.")

if not mobile:
    raise ValueError("Admin mobile cannot be empty.")

if not password:
    raise ValueError("Admin password cannot be empty.")


db = SessionLocal()

try:
    existing = (
        db.query(StaffUser)
        .filter(StaffUser.mobile == mobile)
        .first()
    )

    if existing:
        print("A staff user with this mobile number already exists.")
    else:
        admin = StaffUser(
            name=name,
            mobile=mobile,
            password=hash_password(password),
            role="admin",
            centre_id=None,
        )

        db.add(admin)
        db.commit()
        db.refresh(admin)

        print("\nADMIN CREATED SUCCESSFULLY")
        print("Staff ID :", admin.staff_id)
        print("Name     :", admin.name)
        print("Mobile   :", admin.mobile)
        print("Role     :", admin.role)

finally:
    db.close()