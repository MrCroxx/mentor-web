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

# STATUS CODE

SUCCESS = 20000
BAD = 40000

# CAS

CAS_SERVER = 'https://sso.buaa.edu.cn'
CAS_AFTER_LOGIN = 'index'
SECRET_KEY = "ba926a0379cc9664f3d24151b122d4000031fb75f54e941e6a3334f0b8f0635e"
CAS_LOGIN_ROUTE = '/'
CAS_LOGOUT_ROUTE = '/logout'
CAS_VALIDATE_ROUTE = '/serviceValidate'

# UPLOAD

UPLOADED_XLS_DEST = 'app/static/tmp/xls'
UPLOADED_IMG_DEST = 'app/static/res/user'

# JWT

# JWT_AUTH_URL_RULE = '/jwt/login'
# JWT_EXPIRATION_DELTA = datetime.timedelta(hours=1)
