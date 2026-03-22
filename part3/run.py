from app import create_app, db
from app.models.user import User

app = create_app('config.DevelopmentConfig')

with app.app_context():
    db.create_all()

    # Créer un admin par défaut s'il n'existe pas
    from app.services import facade
    if not facade.get_user_by_email('admin@hbnb.io'):
        admin = User(
            first_name='Admin',
            last_name='HBnB',
            email='admin@hbnb.io',
            password='admin1234',
            is_admin=True
        )
        db.session.add(admin)
        db.session.commit()
        print("Admin créé : admin@hbnb.io / admin1234")

if __name__ == '__main__':
    print("Running on http://127.0.0.1:5000/api/v1/")
    app.run()
