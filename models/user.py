from db import db
from requests import Response, post
from flask import request, url_for
from libs.mailgun import MailGun
from models.confirmation import ConfirmationModel


class UserModel(db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(80), nullable=False)
    email = db.Column(db.String(80), nullable=False, unique=True)
    confirmation = db.relationship("ConfirmationModel", lazy='dynamic', cascade='all, delete-orphan')

    @property
    def most_recent_confirmation(self) -> "ConfirmationModel":
        return self.confirmation.order_by(db.desc(ConfirmationModel.expire_at)).first()

    @classmethod
    def find_by_username(cls, username) -> "UserModel":
        return cls.query.filter_by(username=username).first()

    @classmethod
    def find_by_email(cls, email) -> "UserModel":
        return cls.query.filter_by(email=email).first()

    @classmethod
    def find_by_id(cls, _id) -> "UserModel":
        return cls.query.filter_by(id=_id).first()

    def send_confirmation_email(self) -> Response:
        # http://127.0.0.1:5000/iser_confrim/1
        link = 'test'## request.url_root[:-1] + url_for("confirmation", confirmation_id=self.most_recent_confirmation.id)
        return MailGun.send_confirmation_email(email=[self.email],
                                               subject="Account Activation",
                                               text=f"Please click the link to confirm your registration : {link}",
                                               html="")

    def save_to_db(self) -> None:
        db.session.add(self)
        db.session.commit()

    def delete_from_db(self) -> None:
        db.session.delete(self)
        db.session.commit()
