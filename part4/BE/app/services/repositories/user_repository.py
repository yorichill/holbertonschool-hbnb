from part4.BE.app.models.user import User
from part4.BE.app.persistence.repository import SQLAlchemyRepository


class UserRepository(SQLAlchemyRepository):
    def __init__(self):
        super().__init__(User)

    def get_user_by_email(self, email: str):
        return self.model.query.filter_by(email=email).first()
    