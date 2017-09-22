# -*- coding:utf-8 -*-

from flask import render_template, url_for, redirect, flash, request, abort, session, g, jsonify, Response
from app import app, lm
from sqlalchemy import desc
from flask_jwt import JWT, jwt_required, current_identity
from app.forms import *
from flask_login import login_user, logout_user, login_required, current_user
from urlparse import urlparse, urljoin
from identifyingcode import drawIdentifyingCode
from PIL import Image
from app.models import *
import os
import base64
import math
import json

# Configs and View for Login

lm.login_view = 'login'
lm.login_message = u'W请先登录!'


def is_safe_url(target):
    ref_url = urlparse(request.host_url)
    test_url = urlparse(urljoin(request.host_url, target))
    return test_url.scheme in ('http', 'https') and ref_url.netloc == test_url.netloc


def is_safe_url(next):
    return next


@lm.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


@app.before_request
def before_request():
    g.user = current_user


# normal views


@app.route('/')
@app.route('/index')
def index():
    return render_template('index.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    id = form.id.data
    password = form.password.data
    if form.validate_on_submit():
        u = User.query.filter(User.id == id).first()
        if u is not None:
            if u.testPassword(password):
                login_user(u, form.remember_me.data)
                next = request.args.get('next')
                if next is None:
                    return redirect(url_for('index'))
                if not is_safe_url(next):
                    return abort(400)
                return redirect(next or url_for('index'))
            else:
                flash(u'D密码错误!')
        else:
            flash(u'D该学号或工号不存在!')
    return render_template('login.html', form=form)


# ajax routes

@app.route('/appointment/list/<offset>')
@login_required
def appointment_list(offset):
    user = current_user
    app_list = []
    if user.identify == User.MENTOR:
        Appointment.query.filter(Appointment.men == user).order_by(
            desc(Appointment.submit_time)).offset(offset).limit(10)
    elif user.identify == User.STUDENT:
        Appointment.query.filter(Appointment.stu == user).order_by(
            desc(Appointment.submit_time)).offset(offset).limit(10)


@app.route('/appointment/new', methods=['POST'])
@login_required
def appointment_new():
    pass
