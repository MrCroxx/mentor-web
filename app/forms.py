# -*- coding:utf-8 -*-

from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileRequired, FileAllowed
from wtforms.fields import StringField, PasswordField, BooleanField, IntegerField
from wtforms.validators import DataRequired, Length, Email, EqualTo, NumberRange, Regexp


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


class MentorQueryByDepartmentForm(FlaskForm):
    department = StringField(
        'department',
        validators=[
            DataRequired()
        ]
    )


class MentorQueryByTagForm(FlaskForm):
    tag1 = StringField(
        'tag1',
        validators=[
        ]
    )
    tag2 = StringField(
        'tag2',
        validators=[
        ]
    )


class AppointmentNewForm(FlaskForm):
    description = StringField(
        'description',
    )
    time_date_string = StringField(
        'time_date_string',
        validators=[
            DataRequired(message=u'请选择预约时间!'),
            Regexp(r'(\d+)-(\d+)-(\d+)', message=u'请选择正确的日期!')
        ]
    )


class AppointmentQueryByDepartmentForm(FlaskForm):
    department = StringField(
        'department',
        validators=[
            DataRequired()
        ]
    )


class AppointmentQueryByStatusForm(FlaskForm):
    status = IntegerField(
        'status',
        validators=[
            # DataRequired()
        ]
    )


class AppointmentQueryByDateForm(FlaskForm):
    time_date_string = StringField(
        'time_date_string',
        validators=[
            DataRequired(),
            Regexp(r'(\d+)-(\d+)-(\d+)')
        ]
    )


class AppointmentReplyForm(FlaskForm):
    replytext = StringField(
        'replytext',
        validators=[

        ]
    )
    status = IntegerField(
        'status',
        validators=[
            DataRequired()
        ]
    )


class CourseNewForm(FlaskForm):
    name = StringField(
        'name',
        validators=[
            DataRequired(message=u'请输入1-20字符的课程名!'),
            Length(1, 20, message=u'课程名需要1-20字符!')]
    )
    capacity = IntegerField(
        'capacity',
        validators=[
            DataRequired(message=u'请输入大于0的课程容量!')
        ]
    )
    description = StringField(
        'description',
    )
    time_date_string = StringField(
        'time_date_string',
        validators=[
            DataRequired(message=u'请选择课程日期!'),
            Regexp(r'(\d+)-(\d+)-(\d+)', message=u'请选择正确的日期')
        ]
    )
    time_start_h = IntegerField(
        'time_start_h',
        validators=[]
    )
    time_start_m = IntegerField(
        'time_start_m',
        validators=[]
    )
    time_end_h = IntegerField(
        'time_end_h',
        validators=[]
    )
    time_end_m = IntegerField(
        'time_end_m',
        validators=[]
    )


class CourseQueryByDepartmentForm(FlaskForm):
    department = StringField(
        'department',
        validators=[
            DataRequired()
        ]
    )


class CourseQueryByDateForm(FlaskForm):
    time_date_string = StringField(
        'time_date_string',
        validators=[
            DataRequired(),
            Regexp(r'(\d+)-(\d+)-(\d+)')
        ]
    )
