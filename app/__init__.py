# -*- coding:utf-8 -*-

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_wtf import CSRFProtect
from flask_cas import CAS

app = Flask(__name__)
app.config.from_object('config')
db = SQLAlchemy(app)
lm = LoginManager(app)
CSRFProtect(app)


from app import view, models
CAS(app)

from app.dictionary import write_dynamic_data,reload_dynamic_data
reload_dynamic_data()
# jwt = JWT(app, auth.authenticate, auth.identity)
