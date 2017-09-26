# -*- coding:utf-8 -*-
from random import Random
import hashlib
import time
from datetime import datetime, timedelta
from app import db


def random_str(randomlength=8):
    '''
    获取随机盐值
    :param randomlength:盐值长度
    :return:盐
    '''
    str = ''
    chars = 'AaBbCcDdEeFfGgHhIiJjKkLlMmNnOoPpQqRrSsTtUuVvWwXxYyZz0123456789'
    length = len(chars) - 1
    random = Random()
    for i in range(randomlength):
        str += chars[random.randint(0, length)]
    return str


def getSHA256(content):
    '''
    SHA256加密
    :param content:明文
    :return: 密文
    '''
    SHA256 = hashlib.sha256()
    SHA256.update(content)
    return SHA256.hexdigest()


def getMD5(content):
    '''
    MD5加密(慎用)
    :param content: 明文
    :return: 密文
    '''
    MD5 = hashlib.md5()
    MD5.update(content)
    return MD5.hexdigest()


# 常量
department_to_string = {
    21: u'软件学院',
}

# 多对多关系表
relation_course_student = db.Table('relation_course_student',
                                   db.Column('course_id', db.Integer,
                                             db.ForeignKey('Course.id')),
                                   db.Column('stu_id', db.Integer,
                                             db.ForeignKey('User.id'))
                                   )


class Appointment(db.Model):
    __tablename__ = 'Appointment'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)  # 团体课id 自增主键
    stu_id = db.Column(db.Integer, db.ForeignKey('User.id'))  # 外键 学生id
    men_id = db.Column(db.Integer, db.ForeignKey('User.id'))  # 外键 导师id
    status = db.Column(db.Integer)  # 申请状态
    description = db.Column(db.String)  # 申请理由
    replytext = db.Column(db.String)  # 审批理由
    time_submit = db.Column(db.DateTime)  # 申请时间
    time_reply = db.Column(db.DateTime)  # 审批时间
    location = db.Column(db.String)  # 预约教室
    time_start = db.Column(db.DateTime)  # 预约开始时间
    time_end = db.Column(db.DateTime)  # 预约结束时间

    # 常量
    STATUS_WAITING = 0
    STATUS_PASS = 1
    STATUS_DENY = 2

    def __init__(self, stu, men, description):
        self.stu = stu
        self.men = men
        self.description = description
        self.status = Appointment.STATUS_WAITING
        self.time_submit = datetime.now()

    def toDict(self):
        return {
            'status': self.status,
            'stu_id': self.stu.id,
            'stu_name': self.stu.name,
            'mentor_id': self.men.id,
            'mentor_name': self.men.name,
            'time_submit': self.time_submit.strftime('%Y-%m-%d %H:%M:%S') if self.time_submit else u'暂无数据',
            'time_reply': self.time_reply.strftime('%Y-%m-%d %H:%M:%S') if self.time_reply else u'暂无数据',
            'time_start': self.time_start.strftime('%Y-%m-%d %H:%M:%S') if self.time_start else u'暂无数据',
            'tiem_end': self.tiem_end.strftime('%Y-%m-%d %H:%M:%S') if self.tiem_end else u'暂无数据',
            'description': self.description,
            'replytext': self.replytext,
        }

    def __lt__(self, other):
        return self.time_submit < other.time_submit

    def update(self):
        db.session.add(self)
        db.session.commit()

    def reply(self, status, replytext):
        self.status = status
        self.replytext = replytext
        self.update()

    def delete(self):
        db.session.delete(self)
        db.session.commit()


class Course(db.Model):
    __tablename__ = 'Course'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)  # 团体课id 自增主键
    name = db.Column(db.String, index=True)  # 团体课名称
    department = db.Column(db.Integer)  # 学院id
    men_id = db.Column(db.Integer, db.ForeignKey('User.id'))  # 外键 导师id
    stus = db.relationship('User', secondary=relation_course_student, backref=db.backref(
        'courses_stu', lazy='dynamic'), lazy='dynamic')
    description = db.Column(db.String)  # 课程描述
    location = db.Column(db.String)  # 课程教室
    capacity = db.Column(db.Integer)  # 课程容量
    time_start = db.Column(db.DateTime)  # 课程开始时间
    time_end = db.Column(db.DateTime)  # 课程结束时间
    time_deadline = db.Column(db.DateTime)  # 选课截至时间

    def __init__(self, name, department, men, capacity, description, location, time_start, time_end, time_deadline):
        self.name = name
        self.department = department
        self.men = men
        self.capacity = capacity
        self.description = description
        self.location = location
        self.time_start = time_start
        self.time_end = time_end
        self.time_deadline = time_deadline

    def __lt__(self, other):
        return self.time_start < other.time_start

    def update(self):
        db.session.add(self)
        db.session.commit()

    def addStu(self, stu):
        if stu not in self.stus:
            self.stus.append(stu)
            self.update()

    def removeStu(self, stu):
        if stu in self.stus:
            self.stus.remove(stu)
            self.update()


class User(db.Model):
    __tablename__ = 'User'
    id = db.Column(db.Integer, primary_key=True)  # 学号或工号
    name = db.Column(db.String, index=True)  # 姓名
    salt = db.Column(db.String(8))  # 密码的盐值 防撞库
    passwordhash = db.Column(db.String(64))  # 哈希后的密码
    chpassword = db.Column(db.Boolean)  # 是否修改过密码
    emall = db.Column(db.String)  # 邮箱地址
    emall_confirm = db.Column(db.Boolean)  # 邮箱是否认证
    identify = db.Column(db.Integer)  # 身份(学生/教师)
    department = db.Column(db.Integer)  # 部门ID
    title = db.Column(db.String)  # 职称(教师)
    description = db.Column(db.String)  # 简介(教师)

    appointments_stu = db.relationship('Appointment', backref='stu', foreign_keys=[Appointment.stu_id])
    # 一对多 预约(学生)
    appointments_men = db.relationship('Appointment', backref='men', foreign_keys=[Appointment.men_id])
    # 一对多 预约(导师)
    courses_men = db.relationship('Course', backref='mem', foreign_keys=[Course.men_id])
    # 一对多 团体课(导师)
    # courses_stus 定义见多对多关系表'relation_course_student'与团体课表'Course'
    # 多对多 团体课(学生)

    # 常量
    IDENTIFY_MENTOR = 1
    IDENTIFY_STUDENT = 0

    def __init__(self, id, password, name, identiry, department, title, description):
        self.id = id
        self.setPasswordhash(password, update=False)
        self.name = name
        self.identify = identiry
        self.department = department
        self.title = title
        self.description = description
        self.chpassword = False
        self.emall_confirm = False

    def update(self):
        db.session.add(self)
        db.session.commit()

    def getPasswordhash(self):
        return self.passwordhash

    def setPasswordhash(self, password, update=True):
        self.salt = random_str()
        self.passwordhash = getSHA256(password + self.salt)
        self.chpassword = True
        if update:
            self.update()

    def testPassword(self, password):
        return getSHA256(password + self.salt) == self.passwordhash

    def login(self):
        self.time_lastlogin = datetime.now()
        self.update()

    def getDepartmentString(self):
        return department_to_string[self.department]

    def isMen(self):
        return True if self.identify == User.IDENTIFY_MENTOR else False

    def isStu(self):
        return True if self.identify == User.IDENTIFY_STUDENT else False

    # for flask-login

    def is_authenticated(self):
        return True

    def is_active(self):
        return True

    def is_anonymous(self):
        return False

    def get_id(self):
        return unicode(self.id)
