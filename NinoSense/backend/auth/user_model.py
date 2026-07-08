from flask_login import UserMixin
from backend.database.models import get_user_by_id

class User(UserMixin):
    def __init__(self, user_id, email, name, profile_pic=None, google_id=None):
        self.id = user_id
        self.email = email
        self.name = name
        self.profile_pic = profile_pic
        self.google_id = google_id

    @classmethod
    def get(cls, user_id):
        """
        Retrieves a user from the database by ID and returns a User instance.
        """
        db_user = get_user_by_id(user_id)
        if db_user:
            return cls(
                user_id=db_user['id'],
                email=db_user['email'],
                name=db_user['name'],
                profile_pic=db_user['profile_pic'],
                google_id=db_user['google_id']
            )
        return None
