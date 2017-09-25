# -*- coding:utf-8 -*-

from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileRequired, FileAllowed
from wtforms import StringField, PasswordField, BooleanField, DecimalField
from wtforms.validators import DataRequired, Length, Email, EqualTo, NumberRange


class LoginForm(FlaskForm):
    id = StringField(
        'id',
        validators=[
            DataRequired(message=u'请输入学号或工号!'),
            # NumberRange(min=0, max=99999999, message=u'请输入八位学号!'),
            Length(4, 10, message=u'学号或工号必须在4-10位之间!')
        ]
    )
    password = PasswordField(
        'password',
        validators=[
            DataRequired(message=u'请输入登录密码!'),
            Length(6, 30, message=u'登录密码长度应在6-30个字符内!')
        ]
    )
    remember_me = BooleanField('remember_me', default=False)


class SetPasswordForm(FlaskForm):
    password_old = PasswordField(
        'password_old',
        validators=[
            DataRequired(message=u'请输入旧登录密码!'),
            Length(6, 30, message=u'登录密码长度应在6-30个字符内!')
        ]
    )
    password_new = PasswordField(
        'password_new',
        validators=[
            DataRequired(message=u'请输入新登录密码!'),
            Length(6, 30, message=u'登录密码长度应在6-30个字符内!')
        ]
    )
    password_confirm = PasswordField(
        'password_confirm',
        validators=[
            DataRequired(message=u'请输入新登录密码!'),
            Length(6, 30, message=u'登录密码长度应在6-30个字符内!')
        ]
    )
    identifyingcode = StringField(
        'identifyingcode',
        validators=[
            DataRequired(message=u'请输入4字符的验证码!'),
            Length(4, 4, message=u'请输入4字符的验证码!')
        ]
    )


class AppointmentNewForm(FlaskForm):
    men_id = StringField(
        'men_id',
        validators=[
            Length(4, 10)
        ]
    )
    description = StringField(
        'description',
    )


class AppointmentReplyForm(FlaskForm):
    replytext = StringField(
        'replytext',
    )
    status = BooleanField(
        'status',
    )
