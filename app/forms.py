# -*- coding:utf-8 -*-

from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileRequired, FileAllowed
from wtforms.fields import StringField, PasswordField, BooleanField, IntegerField, SelectMultipleField
from wtforms.validators import DataRequired, Length, Email, EqualTo, NumberRange, Regexp
from app.uploadsets import *


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


class MentorQueryForm(FlaskForm):
    department = StringField(
        'department',
        validators=[
        ]
    )
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
    time_hour = IntegerField(
        'time_hour',
        validators=[
            NumberRange(0, 24, message=u'请选择正确的时间!')
        ]
    )
    time_minute = IntegerField(
        'time_minute',
        validators=[
            NumberRange(0, 60, message=u'请选择正确的时间!')
        ]
    )
    phone = StringField(
        'phone',
        validators=[
            DataRequired(message=u'请填写手机号码!')
        ]
    )


class AppointmentQueryForm(FlaskForm):
    department = StringField(
        'department',
        validators=[
            # DataRequired()
        ]
    )
    status = StringField(
        'status',
        validators=[
            # DataRequired()
        ]
    )
    use_date = BooleanField(
        'use_date',
        validators=[

        ]
    )
    time_date_string = StringField(
        'time_date_string',
        validators=[
            # DataRequired(),
            # Regexp(r'(\d+)-(\d+)-(\d+)')
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
    location = StringField(
        'location',
        validators=[
            DataRequired(message=u'请输入课程地点!')
        ]
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


class ReviewNewForm(FlaskForm):
    location = StringField(
        'location',
        validators=[
            DataRequired(message=u'请填写辅导地点!')
        ]
    )
    type = IntegerField(
        'type',
        validators=[
        ]
    )
    message_stu = StringField(
        'message_stu',
        validators=[
            DataRequired(message=u'请填写学生问题自述!')
        ]
    )

    message_men = StringField(
        'message_men',
        validators=[
            DataRequired(message=u'请填写导师诊断!')
        ]
    )

    message_slu = StringField(
        'message_slu',
        validators=[
            DataRequired(message=u'请填写解决方案!')
        ]
    )


class AdminStudentQueryForm(FlaskForm):
    id = StringField('id')
    name = StringField('name')
    department = StringField('department')
    grade = StringField('grade')


class AdminMentorQueryForm(FlaskForm):
    id = StringField('id')
    name = StringField('name')
    department = StringField('department')


class TagNewForm(FlaskForm):
    tag1id = StringField('tag1id')
    tag1name = StringField('tag1name')
    tag2id = StringField('tag2id')
    tag2name = StringField('tag2name')


class MentorXLSForm(FlaskForm):
    file = FileField(
        'file',
        validators=[
            FileAllowed(xls, u'暂不支持该类型文件上传'),
            FileRequired(u'请选择文件')
        ]
    )


class MentorTagUpdateForm(FlaskForm):
    pass


class AvaTimeAddForm(FlaskForm):
    weekday = IntegerField('weekday')
    time_hour = IntegerField('time_hour')
    time_minute = IntegerField('time_minute')


class MentorInfoUpdateForm(FlaskForm):
    name = StringField('name')
    department_id = StringField('department_id')
    title1 = StringField('title1')
    title2 = StringField('title2')
    xsjz = StringField('xsjz')
    jybj = StringField('jybj')
    yjfx = StringField('yjfx')
    yjjl = StringField('yjjl')
    yjcg = StringField('yjcg')
    gzjl = StringField('gzjl')
    jlry = StringField('jlry')
    fdys = StringField('fdys')
    yjh = StringField('yjh')
    email = StringField('email')
    phone = StringField('phone')
