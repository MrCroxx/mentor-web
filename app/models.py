# -*- coding:utf-8 -*-
from random import Random
import hashlib, time, re
from datetime import datetime, timedelta, date
from app import db
from app.dictionary import *


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


# 多对多关系表
relation_course_student = db.Table('relation_course_student',
                                   db.Column('course_id', db.Integer,
                                             db.ForeignKey('Course.id')),
                                   db.Column('stu_id', db.String,
                                             db.ForeignKey('User.id'))
                                   )

class Department(db.Model):
    __tablename__ = 'Department'
    id = db.Column(db.Integer,primary_key=True,autoincrement=True) # 自增主键 无意义
    d_id = db.Column(db.String)
    d_name = db.Column(db.String)

    def __init__(self,d_id,d_name):
        self.d_id = d_id
        self.d_name = d_name

    def update(self):
        db.session.add(self)
        db.session.commit()

    def getDid(self):
        return self.d_id

    def getDname(self):
        return self.d_name

    def delete(self):
        db.session.delete(self)
        db.session.commit()



class Tag(db.Model):
    __tablename__ = 'Tag'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)  # 自增主键 无意义
    tag1id = db.Column(db.String)
    tag1name = db.Column(db.String)
    tag2id = db.Column(db.String)
    tag2name = db.Column(db.String)

    def __init__(self, tag1id, tag1name, tag2id, tag2name):
        self.tag1id = tag1id
        self.tag2id = tag2id
        self.tag1name = tag1name
        self.tag2name = tag2name

    def update(self):
        db.session.add(self)
        db.session.commit()

    def delete(self):
        db.session.delete(self)
        db.session.commit()


class User2Tag(db.Model):
    __tablename__ = 'User2Tag'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)  # 自增主键 无意义
    men_id = db.Column(db.String)
    tag_id = db.Column(db.Integer)

    def __init__(self, men_id, tag_id):
        self.men_id = men_id
        self.tag_id = tag_id

    def update(self):
        db.session.add(self)
        db.session.commit()

    def delete(self):
        db.session.delete(self)
        db.session.commit()


class MentorAvailableTime(db.Model):
    __tablename__ = 'MentorAvailableTime'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)  # 自增主键 无意义
    men_id = db.Column(db.String, index=True)  # 导师id
    weekday = db.Column(db.Integer)  # 星期n
    time = db.Column(db.Time)  # 时间

    def __init__(self, men_id, weekday, time):
        self.men_id = men_id
        self.weekday = weekday
        self.time = time

    def update(self):
        db.session.add(self)
        db.session.commit()

    def delete(self):
        db.session.delete(self)
        db.session.commit()


class Review(db.Model):
    __tablename__ = 'Review'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    appointment_id = db.Column(db.Integer, db.ForeignKey('Appointment.id'))
    appointment = db.relationship("Appointment", back_populates='review')
    location = db.Column(db.String)
    type = db.Column(db.Integer)
    message_stu = db.Column(db.String)
    message_men = db.Column(db.String)
    message_slu = db.Column(db.String)

    TYPE_OTHER = 0
    TYPE_STUDY = 1
    TYPE_PHY = 2
    TYPE_GRUTH = 3

    def __init__(self, appointment, location, type, m_stu, m_men, m_slu):
        self.appointment = appointment
        self.location = location
        self.type = type
        self.message_stu = m_stu
        self.message_men = m_men
        self.message_slu = m_slu

    def update(self):
        db.session.add(self)
        db.session.commit()

    def getTypeString(self):
        return review_type_id2string[self.type]


class Appointment(db.Model):
    __tablename__ = 'Appointment'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)  # 预约id 自增主键
    stu_id = db.Column(db.String, db.ForeignKey('User.id'))  # 外键 学生id
    men_id = db.Column(db.String, db.ForeignKey('User.id'))  # 外键 导师id
    status = db.Column(db.Integer)  # 申请状态
    description = db.Column(db.String)  # 申请理由
    time_date = db.Column(db.Date)  # 预约日期
    time_time = db.Column(db.DateTime)  # 预约日期+时间
    replytext = db.Column(db.String)  # 审批理由
    location = db.Column(db.String)  # 预约教室
    time_submit = db.Column(db.DateTime)  # 申请时间
    time_reply = db.Column(db.DateTime)  # 审批时间
    score = db.Column(db.Float)  # 预约评分
    phone = db.Column(db.String)  # 学生手机号码
    comment = db.Column(db.String)  # 评价
    review = db.relationship("Review", uselist=False, back_populates="appointment")  # 总结

    # 常量
    STATUS_WAITING = 0
    STATUS_PASS = 1
    STATUS_DENY = 2

    def __init__(self, stu, men, description, time_date, time_time, phone):
        self.stu = stu
        self.men = men
        self.description = description
        self.status = Appointment.STATUS_WAITING
        self.time_submit = datetime.now()
        self.time_date = time_date
        self.score = 0
        self.time_time = time_time
        self.phone = phone

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
            'time_date': self.time_time.strftime("%Y-%m-%d %H:%M") if self.time_date else u'暂无数据',
            'score': self.score,
            'phone': self.phone,
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

    def setScore(self, score, comment):
        self.score = score
        self.comment = comment
        self.men.score_all += score
        self.men.score_times += 1
        self.men.update()
        self.update()

    def hasReview(self):
        return self.review is not None


class Course(db.Model):
    __tablename__ = 'Course'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)  # 团体课id 自增主键
    name = db.Column(db.String, index=True)  # 团体课名称
    men_id = db.Column(db.String, db.ForeignKey('User.id'))  # 外键 导师id
    stus = db.relationship('User', secondary=relation_course_student, backref=db.backref(
        'courses_stu', lazy='dynamic'), lazy='dynamic')
    description = db.Column(db.String)  # 课程描述
    location = db.Column(db.String)  # 课程教室
    capacity = db.Column(db.Integer)  # 课程容量
    time_start = db.Column(db.DateTime)  # 课程开始时间
    time_end = db.Column(db.DateTime)  # 课程结束时间
    time_submit = db.Column(db.DateTime)
    replytext = db.Column(db.String)
    status = db.Column(db.Integer)

    STATUS_WAITING = 0
    STATUS_PASS = 1
    STATUS_DENY = 2

    def __init__(self, name, men, capacity, description, time_start, time_end):
        self.name = name
        self.men = men
        self.capacity = capacity
        self.description = description
        self.time_start = time_start
        self.time_end = time_end
        self.status = Course.STATUS_WAITING
        self.time_submit = datetime.now()

    def update(self):
        db.session.add(self)
        db.session.commit()

    def delete(self):
        db.session.delete(self)
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
        return department_id2name[self.department]

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
            'signstatus': 0 if user is None else (1 if self.isSigned(user) else 0),
            'status': self.status,
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
    department = db.Column(db.String)  # 部门ID
    title = db.Column(db.String)  # 职称(教师)
    description = db.Column(db.String)  # 简介(教师)
    tag1 = db.Column(db.String)  # 一级标签
    tag2 = db.Column(db.String)  # 二级标签
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
    IDENTIFY_ADMIN = 2

    def __init__(self, id, password, name, identiry, department, tag1, tag2, title, description):
        self.id = id
        self.setPasswordhash(password, update=False)
        self.name = name
        self.identify = identiry
        self.department = department
        self.tag1 = tag1
        self.tag2 = tag2
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
            'department': department_id2name[self.department],
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
        return department_id2name[self.department]

    def getTagString(self):
        uts = User2Tag.query.filter(User2Tag.men_id == self.id).all()
        tags = []
        for ut in uts:
            tags.append(Tag.query.filter(Tag.id == ut.tag_id).first())
        s = ''
        for tag in tags:
            s += '[%s]%s,' % (tag.tag1name, tag.tag2name)
        return s

    def isMen(self):
        return True if self.identify == User.IDENTIFY_MENTOR else False

    def isStu(self):
        return True if self.identify == User.IDENTIFY_STUDENT else False

    def isAdmin(self):
        return True if self.identify == User.IDENTIFY_ADMIN else False

    def getHTMLDescription(self, admin=False):
        description = self.description.replace('\n', '<br />')
        if admin:
            description += u'<div class="btn btn-primary" data-toggle="modal"data-target="#update-info" style="width: 100%">修改基本信息</div>'
        description += self.getAvailableTime(admin)
        return description

    def getAvailableTime(self, admin):
        text = ''
        times = MentorAvailableTime.query.filter(
            MentorAvailableTime.men_id == self.id).order_by(
            MentorAvailableTime.weekday, MentorAvailableTime.time).all()

        text += u'<h3>可预约时间</h3>'
        if len(times) == 0:
            text += u'<p>暂无限制</p>'
        for time in times:
            btn = u'' if not admin else u"&nbsp;&nbsp;&nbsp;&nbsp;<a href='/admin/user/%s/avatime/%s/delete' class='btn btn-danger btn-sm'>删除</a>" % (
                self.id, time.id)

            text += u'<p>星期%s %s%s</p>' % (weekday_int2char[time.weekday], time.time.strftime('%H:%M'), btn)

        if admin:
            text += u'<div class="btn btn-primary" data-toggle="modal" data-target="#add-avatime">添加可预约时间</div>'

        return text

    def canAccessData(self):
        if self.identify == User.IDENTIFY_ADMIN:
            return True
        return self.id in data_access_ids

    def getAppointmentCount(self):
        if self.identify == User.IDENTIFY_STUDENT:
            return len(self.appointments_stu)
        elif self.identify == User.IDENTIFY_MENTOR:
            return len(self.appointments_men)
        else:
            return 0

    def getTagOptions(self):
        l = []
        tagids = []
        uts = User2Tag.query.filter(User2Tag.men_id == self.id).all()
        for ut in uts:
            tag = Tag.query.filter(Tag.id == ut.tag_id).first()
            tagids.append(tag.id)
        tags = Tag.query.order_by(Tag.tag1id, Tag.tag2id).all()
        for tag in tags:
            l.append('<input type="checkbox" name="tags" value="%s" %s/>[%s]%s' % (
                tag.id, "checked" if tag.id in tagids else "", tag.tag1name, tag.tag2name))
        return l

    # for flask-login

    def is_authenticated(self):
        return True

    def is_active(self):
        return True

    def is_anonymous(self):
        return False

    def get_id(self):
        return unicode(self.id)


# DYNAMIC

def getOptions_tag1():
    s = u'<option value="ALL" selected="selected">全部</option>'
    tag_set = set()
    tags = Tag.query.all()
    for tag in tags:
        tag_set.add((tag.tag1id, tag.tag1name))
    for tag in tag_set:
        s += u'<option value="%s">%s</option>' % (tag[0], tag[1])
    return s


def getOptions_tag2():
    s = u'<option value="ALL" selected="selected">全部</option>'
    tag_set = set()
    tags = Tag.query.all()
    for tag in tags:
        tag_set.add((tag.tag2id, tag.tag2name))
    for tag in tag_set:
        s += u'<option value="%s">%s</option>' % (tag[0], tag[1])
    return s
