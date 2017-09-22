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
SECRET_KEY = "04c47cc2f0e4a472a3fff1c19cc96c4e2f2901a1396d6b7e5a993769511ca1e5"

# JWT

# JWT_AUTH_URL_RULE = '/jwt/login'
# JWT_EXPIRATION_DELTA = datetime.timedelta(hours=1)
