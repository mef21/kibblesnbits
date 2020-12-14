from flask_login import UserMixin
from datetime import datetime
from . import db, login_manager
from . import config
from .utils import current_time
import base64
import pyotp

@login_manager.user_loader
def load_user(user_id):
    return User.objects(username=user_id).first()


class User(db.Document, UserMixin):
    username = db.StringField(required=True, unique=True)
    email = db.EmailField(required=True, unique=True)
    password = db.StringField(required=True)
    profile_pic = db.ImageField()
    otp_secret = db.StringField(required=True, min_length=16, max_length=16, default=pyotp.random_base32())

    # Returns unique string identifying our object
    def get_id(self):
        return self.username


class Review(db.Document):
    commenter = db.ReferenceField(User, required=True)
    content = db.StringField(required=True, min_length=5, max_length=500)
    date = db.StringField(required=True)
    id_url = db.StringField(required=True) # TODO
    dog_title = db.StringField(required=True, min_length=1, max_length=100)

class Post(db.Document):
    poster = db.ReferenceField(User, required=True)
    text1 = db.StringField(required=True, min_length=5, max_length=500)
    date = db.StringField(required=True)
    pic = db.ImageField()


class Poll(db.Document):
    date = db.StringField(required=True)
    dog1 = db.StringField(required=True)
    dog2 = db.StringField(required=True)
    dog1_vote_count = db.IntField(required=True)
    dog2_vote_count = db.IntField(required=True)

class Vote(db.Document):
    date = db.StringField(required=True)
    user = db.ReferenceField(User, required=True)
    v = db.IntField(required=True)

