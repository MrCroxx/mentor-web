# -*- coding:utf-8 -*-
from random import Random
import hashlib
import time
import datetime
from app import db


def random_str(randomlength=8):
    str = ''
    chars = 'AaBbCcDdEeFfGgHhIiJjKkLlMmNnOoPpQqRrSsTtUuVvWwXxYyZz0123456789'
    length = len(chars) - 1
    random = Random()
    for i in range(randomlength):
        str += chars[random.randint(0, length)]
    return str


def getSHA256(content):
    SHA256 = hashlib.sha256()
    SHA256.update(content)
    return SHA256.hexdigest()


def getMD5(content):
    MD5 = hashlib.md5()
    MD5.update(content)
    return MD5.hexdigest()


class User(db.Model):
    __tablename__ = 'user'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, index=True)
    passwordhash = db.Column(db.String(64))
    salt = db.Column(db.String(8))
    sex = db.Column(db.Integer)
    phonenum = db.Column(db.String)
    identiry = db.Column(db.Integer)

    appointments_stu = db.relationship('appointment', backref='stu')
    appointments_men = db.relationship('appointment', backref='men')

    def __init__(self, id, password):
        self.id = id
        self.setPasswordhash(password)

    def update(self):
        db.session.add(self)
        db.session.commit()

    def getPasswordhash(self):
        return self.passwordhash

    def setPasswordhash(self, password):
        self.salt = random_str()
        self.passwordhash = getSHA256(password + self.salt)
        self.update()

    def testPassword(self, password):
        return getSHA256(password + self.salt) == self.passwordhash

    # for flask-login

    def is_authenticated(self):
        return True

    def is_active(self):
        return True

    def is_anonymous(self):
        return False

    def get_id(self):
        return unicode(self.id)


class Appointment(db.Model):
    __tablename__ = 'appointment'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    stu_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    men_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    description = db.Column(db.Text)
    status = db.Column(db.Integer)
    reply = db.Column(db.Text)
    submit_time = db.Column(db.DateTime)
    reply_time = db.Column(db.DateTime)

    def __init__(self, stu, men):
        self.stu = stu
        self.men = men
        pass

    def update(self):
        db.session.add(self)
        db.session.commit()


'''

relation_course_teacher = db.Table('relation_course_teacher',
                                   db.Column('course_id', db.Integer,
                                             db.ForeignKey('Course.id')),
                                   db.Column('teacher_id', db.Integer,
                                             db.ForeignKey('User.id'))
                                   )

relation_course_student = db.Table('relation_course_student',
                                   db.Column('course_id', db.Integer,
                                             db.ForeignKey('Course.id')),
                                   db.Column('student_id', db.Integer,
                                             db.ForeignKey('User.id'))
                                   )


class User(db.Model):

    __tablename__ = 'User'
    id = db.Column(db.Integer, primary_key=True)
    nickname = db.Column(db.String(64), index=True)
    passwordhash = db.Column(db.String(64))
    salt = db.Column(db.String(8))
    submit_time = db.Column(db.DateTime)
    sex = db.Column(db.Integer)
    department = db.Column(db.String(30))

    # 0-female
    # 1-male
    # 2-unknown

    # permission = db.Column(db.Integer)

    # @permission:
    # byte-0:is authorized
    # byte-1:is student
    # byte-2:is teacher
    # byte-3:is admin

    admined_courses = db.relationship('Course', backref='admin')
    signs = db.relationship('Sign', backref='student')
    use_face = db.Column(db.Boolean)
    use_voice = db.Column(db.Boolean)

    def __init__(self, _id, _nickname, _password, _department):
        self.id = _id
        self.nickname = _nickname
        self.salt = random_str()
        self.passwordhash = getSHA256(_password + self.salt)
        self.submit_time = datetime.datetime.now()
        self.sex = 2
        self.permission = 0
        self.department = _department
        self.use_voice = False
        self.use_face = False

    def __repr__(self):
        return '<User %r %r %r>' % (self.id, self.nickname, self.submit_time)

    def addPermission(self, _chp):
        self.permission = self.permission | _chp
        db.session.add(self)
        db.session.commit()

    def subPermission(self, _chp):
        _chp = ~_chp
        self.permission = self.permission & _chp
        db.session.add(self)
        db.session.commit()

    def testPermission(self, _p):
        tmp = _p & self.permission
        if _p == tmp:
            return True
        else:
            return False

    def getPasswordhash(self):
        return self.passwordhash

    def setPasswordhash(self, _password):
        self.salt = random_str()
        self.passwordhash = getSHA256(_password + self.salt)
        db.session.add(self)
        db.session.commit()

    def testPassword(self, _password):
        return getSHA256(_password + self.salt) == self.passwordhash

    def setUserInfo(self, _nickname, _department, _sex):
        self.nickname = _nickname
        self.department = _department
        self._sex = _sex
        db.session.add(self)
        db.session.commit()

    def enableFace(self):
        self.use_face = True
        db.session.add(self)
        db.session.commit()

    def enableVoice(self):
        self.use_voice = True
        db.session.add(self)
        db.session.commit()

    def disableFace(self):
        self.use_face = False
        db.session.add(self)
        db.session.commit()

    def disableVoice(self):
        self.useVoice = False
        db.session.add(self)
        db.session.commit()

    # for flask-login

    def is_authenticated(self):
        return True

    def is_active(self):
        return True

    def is_anonymous(self):
        return False

    def get_id(self):
        return unicode(self.id)


class Course(db.Model):

    __tablename__ = 'Course'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), index=True)
    discription = db.Column(db.String(120))
    teachers = db.relationship('User', secondary=relation_course_teacher, backref=db.backref(
        'owned_courses', lazy='dynamic'), lazy='dynamic')
    students = db.relationship('User', secondary=relation_course_student, backref=db.backref(
        'signed_courses', lazy='dynamic'), lazy='dynamic')
    admin_id = db.Column(db.Integer, db.ForeignKey('User.id'))
    acts = db.relationship('Act', backref='course')
    start_time = db.Column(db.DateTime)

    def __init__(self, _name, _admin):
        self.name = _name
        self.admin = _admin
        self.start_time = datetime.datetime.now()

    def __repr__(self):
        return '<Course %r %r %r>' % (self.id, self.name, self.admin_id)


class Act(db.Model):

    __tablename__ = 'Act'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64))
    start_time = db.Column(db.DateTime)
    stop_time = db.Column(db.DateTime)
    course_id = db.Column(db.Integer, db.ForeignKey('Course.id'))
    signs = db.relationship('Sign', backref='act')
    use_gps = db.Column(db.Boolean)
    use_face = db.Column(db.Boolean)
    use_voice = db.Column(db.Boolean)
    gps_lo = db.Column(db.Float)
    gps_di = db.Column(db.Float)

    def __init__(self, _name, _course, _use_gps, _use_face, _use_voice):
        self.name = _name
        self.course = _course
        self.use_gps = _use_gps
        self.use_face = _use_face
        self.use_voice = _use_voice
        self.start_time = datetime.datetime.now()
        self.stop_time = datetime.datetime.now() + datetime.timedelta(days=1)

    def __repr__(self):
        return '<Act %r %r %r>' % (self.id, self.name, self.course.name)

    def setGPSLocation(self, _lo, _di):
        self.gps_lo = _lo
        self.gps_di = _di
        db.session.add(self)
        db.session.commit()

    def stopSigning(self):
        self.stop_time = datetime.datetime.now()
        db.session.add(self)
        db.session.commit()

    def getUnsignedStudents(self):
        c = self.course
        stus = c.students.all()
        for s in self.signs:
            stus.remove(s.student)
        return stus


class Sign(db.Model):

    __tablename__ = 'Sign'
    id = db.Column(db.Integer, primary_key=True)
    sign_time = db.Column(db.DateTime)
    act_id = db.Column(db.Integer, db.ForeignKey('Act.id'))
    stu_id = db.Column(db.Integer, db.ForeignKey('User.id'))

    def __init__(self, _act, _stu):
        self.act = _act
        self.student = _stu
        self.sign_time = datetime.datetime.now()

    def __repr__(self):
        return '<Sign %r %r %r>' % (self.id, self.act.name, self.student.nickname)
'''
