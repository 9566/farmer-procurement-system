import os
from database import SessionLocal, Base, engine
from models import StaffUser, ProcurementCentre, Crop
from auth import hash_password

def setup():
    # Base.metadata.create_all(bind=engine) # this is already in main.py, but safe to run here
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    
    # 1. Admin
    admin = db.query(StaffUser).filter_by(mobile='9999999999').first()
    if not admin:
        admin = StaffUser(
            name='Admin User',
            mobile='9999999999',
            password=hash_password('admin123'),
            role='admin'
        )
        db.add(admin)
    
    # 2. Procurement Centre
    centre = db.query(ProcurementCentre).filter_by(centre_name='Lucknow Mandi Centre').first()
    if not centre:
        centre = ProcurementCentre(
            centre_name='Lucknow Mandi Centre',
            location='Sector 5, Lucknow',
            district='Lucknow',
            capacity_per_day=100,
        )
        db.add(centre)
        
    # 3. Crops
    crops = [
        {'crop_name': 'Wheat', 'minimum_support_price': 2275.00, 'unit': 'quintal'},
        {'crop_name': 'Rice', 'minimum_support_price': 2183.00, 'unit': 'quintal'},
        {'crop_name': 'Sugarcane', 'minimum_support_price': 340.00, 'unit': 'quintal'},
    ]
    for c in crops:
        crop = db.query(Crop).filter_by(crop_name=c['crop_name']).first()
        if not crop:
            db.add(Crop(**c))

    db.commit()
    db.close()
    print("Database setup complete.")

if __name__ == '__main__':
    setup()
