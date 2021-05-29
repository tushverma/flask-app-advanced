from typing import List
from requests import Response, post
import os


class MailGunException(Exception):
    def __init__(self, message: str):
        super().__init__(message)


class MailGun:
    MAILGUN_DOMAIN = os.environ.get('MAILGUN_DOMAIN')
    MAILGUN_API_KEY = os.environ.get('MAILGUN_API_KEY')
    FROM_EMAIL = "tpostmaster@sandbox51286b7df2e44b82ae4aacda4c78e934.mailgun.org"

    @classmethod
    def send_confirmation_email(cls, email: List[str], subject: str, text: str, html: str) -> Response:
        if cls.MAILGUN_API_KEY is None:
            raise MailGunException("Failed to load MailGun Api Key")
        if cls.MAILGUN_DOMAIN is None:
            raise MailGunException("Failed to load MailGun Domain")
        response = post(
            f"https://api.mailgun.net/v3/{cls.MAILGUN_DOMAIN}/messages",
            auth=("api", cls.MAILGUN_API_KEY),
            data={"from": f"Tushar Verma <{cls.FROM_EMAIL}>",
                  "to": email,
                  "subject": subject,
                  "text": text,
                  "html": html,
                  }
        )
        if response.status_code != 200:
            raise MailGunException('Error in sending email')
