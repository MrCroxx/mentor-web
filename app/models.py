# -*- coding:utf-8 -*-
from random import Random
import hashlib
import time
from datetime import datetime,timedelta
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


class Appointment(db.Model):
    __tablename__ = 'Appointment'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    stu_id = db.Column(db.Integer, db.ForeignKey('User.id'))
    men_id = db.Column(db.Integer, db.ForeignKey('User.id'))
    description = db.Column(db.Text)
    status = db.Column(db.Integer)
    replytext = db.Column(db.Text)
    submit_time = db.Column(db.DateTime)
    reply_time = db.Column(db.DateTime)

    WAITING = 0
    PASS = 1
    DENY = 2

    def __init__(self, stu, men, description):
        self.stu = stu
        self.men = men
        self.description = description
        status = Appointment.WAITING
        self.submit_time = datetime.now()

    def update(self):
        db.session.add(self)
        db.session.commit()

    def reply(self,status,replytext):
        self.status=status
        self.replytext = replytext
        self.update()


class User(db.Model):
    __tablename__ = 'User'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, index=True)
    passwordhash = db.Column(db.String(64))
    salt = db.Column(db.String(8))
    sex = db.Column(db.Integer)
    phonenum = db.Column(db.String)
    identify = db.Column(db.Integer)

    appointments_stu = db.relationship('Appointment', backref='stu', foreign_keys=[Appointment.stu_id])
    appointments_men = db.relationship('Appointment', backref='men', foreign_keys=[Appointment.men_id])

    MENTOR = 1
    STUDENT = 0

    MALE = 1
    FEMALE = 0

    def __init__(self, id, password, name, sex, phonenum, identiry):
        self.id = id
        self.setPasswordhash(password, update=False)
        self.name = name
        self.sex = sex
        self.phonenum = phonenum
        self.identify = identiry

    def update(self):
        db.session.add(self)
        db.session.commit()

    def getPasswordhash(self):
        return self.passwordhash

    def setPasswordhash(self, password, update=True):
        self.salt = random_str()
        if update:
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
