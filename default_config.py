import os

DEBUG = True
SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL')
SQLALCHEMY_TRACK_MODIFICATIONS = False
PROPAGATE_EXCEPTIONS = True
JWT_SECRET_KEY = os.environ['JWT_SECRET_KEY']
SECRET_KEY = os.environ['APP_SECRET_KEY']
UPLOADED_IMAGES_DEST = os.path.join("static", "images") # should be equal to image_helper.image_set
JWT_BLACKLIST_ENABLED = True
JWT_BLACKLIST_TOKEN_CHECKS = ["access", "refresh"]

