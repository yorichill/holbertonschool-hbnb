"""
seed.py — Populate the database with initial data.
Run once after db.create_all():  python seed.py
"""
from app import create_app, db
from app.models.user    import User
from app.models.amenity import Amenity

ADMIN_EMAIL = 'admin@hbnb.io'
ADMIN_PWD   = 'admin1234'

AMENITIES = ['WiFi', 'Swimming Pool', 'Air Conditioning', 'Parking', 'Kitchen']


def seed():
    app = create_app()
    with app.app_context():
        db.create_all()

        # ── Admin user ────────────────────────────────────────────────────
        if not User.query.filter_by(email=ADMIN_EMAIL).first():
            admin = User(
                first_name='Admin',
                last_name='HBnB',
                email=ADMIN_EMAIL,
                is_admin=True,
            )
            admin.hash_password(ADMIN_PWD)
            db.session.add(admin)
            print(f'[seed] Admin created: {ADMIN_EMAIL}')
        else:
            print(f'[seed] Admin already exists, skipping.')

        # ── Amenities ─────────────────────────────────────────────────────
        for name in AMENITIES:
            if not Amenity.query.filter_by(name=name).first():
                db.session.add(Amenity(name=name))
                print(f'[seed] Amenity created: {name}')

        db.session.commit()
        print('[seed] Done.')


if __name__ == '__main__':
    seed()