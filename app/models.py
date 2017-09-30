# -*- coding:utf-8 -*-
from random import Random
import hashlib
import time
from datetime import datetime, timedelta, date
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
    1: u'材料科学与工程学院',
    2: u'电子信息工程学院',
    3: u'自动化科学与电气工程学院',
    4: u'能源与动力工程学院',
    5: u'航空科学与工程学院',
    6: u'计算机学院',
    7: u'机械工程及自动化学院',
    8: u'经济管理学院',
    9: u'数学与系统科学学院',
    10: u'生物与医学工程学院',
    11: u'人文社会科学学院',
    12: u'外国语学院',
    13: u'交通科学与工程学院',
    14: u'可靠性与系统工程学院',
    15: u'宇航学院',
    16: u'飞行学院',
    17: u'仪器科学与光电工程学院',
    18: u'北京学院',
    19: u'物理科学与核能工程学院',
    20: u'法学院',
    21: u'软件学院',
    22: u'现代远程教育学院',
    23: u'高等理工学院',
    24: u'中法工程师学院',
    25: u'国际学院',
    26: u'新媒体艺术与设计学院',
    27: u'化学与环境学院',
    28: u'马克思主义学院',
    29: u'人文与社会科学高等研究院',
    30: u'空间与环境学院',
    35: u'国际通用工程学院',
    37: u'北航学院',
    73: u'士谔书院',
    74: u'冯如书院',
    75: u'士嘉书院',
    76: u'守锷书院',
    77: u'致真书院',
    79: u'知行书院',
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
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)  # 预约id 自增主键
    stu_id = db.Column(db.Integer, db.ForeignKey('User.id'))  # 外键 学生id
    men_id = db.Column(db.Integer, db.ForeignKey('User.id'))  # 外键 导师id
    status = db.Column(db.Integer)  # 申请状态
    description = db.Column(db.String)  # 申请理由
    time_date = db.Column(db.Date)  # 预约时间
    replytext = db.Column(db.String)  # 审批理由
    location = db.Column(db.String)  # 预约教室
    time_submit = db.Column(db.DateTime)  # 申请时间
    time_reply = db.Column(db.DateTime)  # 审批时间
    score = db.Column(db.Float)  # 预约评分

    # 常量
    STATUS_WAITING = 0
    STATUS_PASS = 1
    STATUS_DENY = 2

    def __init__(self, stu, men, description, time_date):
        self.stu = stu
        self.men = men
        self.description = description
        self.status = Appointment.STATUS_WAITING
        self.time_submit = datetime.now()
        self.time_date = time_date
        self.score = 0

    def toDict(self):
        return {
            'id': self.id,
            'status': self.status,
            'stu_id': self.stu.id,
            'stu_name': self.stu.name,
            'men_id': self.men.id,
            'men_name': self.men.name,
            'time_submit': self.time_submit.strftime('%Y-%m-%d %H:%M:%S') if self.time_submit else u'暂无数据',
            'time_reply': self.time_reply.strftime('%Y-%m-%d %H:%M:%S') if self.time_reply else u'暂无数据',
            'description': self.description if self.description else u'暂无数据',
            'replytext': self.replytext if self.replytext else u'暂无数据',
            'location': self.location if self.location else u'暂无数据',
            'time_date': self.time_date.strftime("%Y-%m-%d") if self.time_date else u'暂无数据',
            'score': self.score,
        }

    def update(self):
        db.session.add(self)
        db.session.commit()

    def reply(self, status, replytext, location):
        self.status = status
        self.replytext = replytext
        self.location = location
        self.time_reply = datetime.now()
        self.update()

    def delete(self):
        db.session.delete(self)
        db.session.commit()

    def canScore(self):
        # return (datetime.now().date() > self.time_date) and (self.status == Appointment.STATUS_PASS) and (self.score==0)
        return (self.status == Appointment.STATUS_PASS) and (self.score == 0)

    def setScore(self, score):
        self.score = score
        self.men.score_all += score
        self.men.score_times += 1
        self.men.update()
        self.update()


class Course(db.Model):
    __tablename__ = 'Course'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)  # 团体课id 自增主键
    name = db.Column(db.String, index=True)  # 团体课名称
    men_id = db.Column(db.Integer, db.ForeignKey('User.id'))  # 外键 导师id
    stus = db.relationship('User', secondary=relation_course_student, backref=db.backref(
        'courses_stu', lazy='dynamic'), lazy='dynamic')
    description = db.Column(db.String)  # 课程描述
    location = db.Column(db.String)  # 课程教室
    capacity = db.Column(db.Integer)  # 课程容量
    time_start = db.Column(db.DateTime)  # 课程开始时间
    time_end = db.Column(db.DateTime)  # 课程结束时间
    time_submit = db.Column(db.DateTime)

    def __init__(self, name, men, capacity, description, time_start, time_end):
        self.name = name
        self.men = men
        self.capacity = capacity
        self.description = description
        self.time_start = time_start
        self.time_end = time_end
        self.time_submit = datetime.now()

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

    def getSignedNum(self):
        return self.stus.count()

    def getDepartmentString(self):
        return department_to_string[self.department]

    def full(self):
        return self.stus.count() >= self.capacity

    def isSigned(self, user):
        return user in self.stus.all()

    def sign(self, user):
        if not self.isSigned(user):
            self.stus.append(user)
            self.update()
            return True
        return False

    def unsign(self, user):
        if self.isSigned(user):
            self.stus.remove(user)
            self.update()
            return True
        return False

    def toDict(self, user=None):
        return {
            'id': self.id,
            'name': self.name,
            'men_name': self.men.name,
            'description': self.description,
            'location': self.location if self.location else u'暂无数据',
            'capacity': self.capacity,
            'signednum': self.getSignedNum(),
            'time_start': self.time_start.strftime('%Y-%m-%d %H:%M:%S'),
            'time_end': self.time_end.strftime('%Y-%m-%d %H:%M:%S'),
            'time_sumbit': self.time_submit.strftime('%Y-%m-%d %H:%M:%S'),
            'status': 0 if user is None else (1 if self.isSigned(user) else 0),
        }


class User(db.Model):
    __tablename__ = 'User'
    id_key = db.Column(db.Integer, primary_key=True, autoincrement=True)
    id = db.Column(db.String, unique=True, index=True)  # 学号或工号
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
    score_all = db.Column(db.Float)  # 评分(总)
    score_times = db.Column(db.Integer)  # 评分次数

    appointments_stu = db.relationship('Appointment', backref='stu', foreign_keys=[Appointment.stu_id])
    # 一对多 预约(学生)
    appointments_men = db.relationship('Appointment', backref='men', foreign_keys=[Appointment.men_id])
    # 一对多 预约(导师)
    courses_men = db.relationship('Course', backref='men', foreign_keys=[Course.men_id])
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
        self.score_all = 0
        self.score_times = 0

    def toDict(self):
        return {
            'id': self.id,
            'name': self.name,
            'department': department_to_string[self.department],
            'title': self.title,
            'description': self.description,
            'appointment_num': len(self.appointments_men),
            'score': (self.score_all / self.score_times) if self.score_times > 0 else u'暂无数据',
        }

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
