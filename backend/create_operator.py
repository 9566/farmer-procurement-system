import getpass

from database import SessionLocal
from models import StaffUser, ProcurementCentre
from auth import hash_password


name = input("Operator name: ").strip()
mobile = input("Operator mobile: ").strip()
password = getpass.getpass("Operator password: ")

centre_input = input("Centre ID: ").strip()


# ------------------------------------------------------------
# VALIDATION
# ------------------------------------------------------------

if not name:
    raise ValueError("Operator name cannot be empty.")

if not mobile:
    raise ValueError("Operator mobile cannot be empty.")

if not password:
    raise ValueError("Operator password cannot be empty.")

if not centre_input:
    raise ValueError("Centre ID is required for an operator.")

try:
    centre_id = int(centre_input)
except ValueError:
    raise ValueError("Centre ID must be a valid number.")


# ------------------------------------------------------------
# DATABASE
# ------------------------------------------------------------

db = SessionLocal()

try:

    # Check if mobile already exists
    existing_staff = (
        db.query(StaffUser)
        .filter(StaffUser.mobile == mobile)
        .first()
    )

    if existing_staff:
        print("\nA staff user with this mobile number already exists.")
        print("Staff ID :", existing_staff.staff_id)
        print("Role     :", existing_staff.role)
        raise SystemExit(0)

    # Check procurement centre
    centre = (
        db.query(ProcurementCentre)
        .filter(ProcurementCentre.centre_id == centre_id)
        .first()
    )

    if not centre:
        raise ValueError(
            f"Procurement centre with ID {centre_id} does not exist."
        )

    # --------------------------------------------------------
    # CREATE OPERATOR
    # --------------------------------------------------------

    operator = StaffUser(
        name=name,
        mobile=mobile,
        password=hash_password(password),
        role="operator",
        centre_id=centre_id,
    )

    db.add(operator)
    db.commit()
    db.refresh(operator)

    print("\n====================================")
    print("OPERATOR CREATED SUCCESSFULLY")
    print("====================================")
    print("Staff ID :", operator.staff_id)
    print("Name     :", operator.name)
    print("Mobile   :", operator.mobile)
    print("Role     :", operator.role)
    print("Centre ID:", operator.centre_id)
    print("Centre   :", centre.centre_name)
    print("====================================")

except Exception:
    db.rollback()
    raise

finally:
    db.close()