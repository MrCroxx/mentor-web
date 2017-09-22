# -*- coding:utf-8 -*-

import os
import datetime

# SQLALCHEMY

basedir = os.path.abspath(os.path.dirname(__file__))

BASE_DIR = basedir

SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(basedir, 'mentor.db')
SQLALCHEMY_TRACK_MODIFICATIONS = False

# FORM

CSRF_ENABLED = True
SECRET_KEY = "ba926a0379cc9664f3d24151b122d4000031fb75f54e941e6a3334f0b8f0635e"

# JWT

# JWT_AUTH_URL_RULE = '/jwt/login'
# JWT_EXPIRATION_DELTA = datetime.timedelta(hours=1)
