# -*- coding:utf-8 -*-

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_wtf import CSRFProtect
from flask_cas import CAS
import cx_Oracle
import os
from app.secret import *
import sys
reload(sys)
sys.setdefaultencoding("utf-8")

os.environ['NLS_LANG'] = 'SIMPLIFIED CHINESE_CHINA.UTF8'

app = Flask(__name__)
app.config.from_object('config')
db = SQLAlchemy(app)
lm = LoginManager(app)
CSRFProtect(app)
# oracle_db = cx_Oracle.connect(ORACLE_CONN)

from app import view, models
CAS(app)
