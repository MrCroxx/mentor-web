# -*- coding:utf-8 -*-

import xlwt, os
from app.models import *


def generateData(appointments, path):
    workbook = xlwt.Workbook(encoding='utf-8')
    sheet = workbook.add_sheet('Appointments')
    data = []
    data.append([u'导师工号', u'导师姓名', u'学生学号', u'学生姓名', u'提交日期', u'预约日期',
                 u'申请状态', u'申请理由', u'导师回复', ])

    for appointment in appointments:
        rowdata = [appointment.men.id, appointment.men.name, appointment.stu.id, appointment.stu.name,
                   appointment.time_submit.strftime('%Y-%m-%d %H:%M:%S'),
                   appointment.time_time.strftime('%Y-%m-%d %H:%M:%S'),
                   u'申请中' if appointment.status == Appointment.STATUS_WAITING else(
                       u'通过' if appointment.status == Appointment.STATUS_PASS else u'未通过'
                   ),
                   appointment.description, appointment.replytext]
        data.append(rowdata)

    for row in range(len(data)):
        for col in range(len(data[row])):
            sheet.write(row, col, data[row][col])

    workbook.save(path)


def adminGenerateAppointment(appointments, path):
    workbook = xlwt.Workbook(encoding='utf-8')
    sheet = workbook.add_sheet('Appointments')
    data = []
    data.append([u'导师工号', u'导师姓名', u'学生学号', u'学生姓名', u'提交日期', u'预约日期',
                 u'申请状态', u'申请理由', u'导师回复',
                 u'学生评分', u'学生评价',
                 u'辅导地点', u'辅导类型', u'学生自述', u'问题诊断', u'解决方案'])

    for appointment in appointments:
        rowdata = [appointment.men.id, appointment.men.name, appointment.stu.id, appointment.stu.name,
                   appointment.time_submit.strftime('%Y-%m-%d %H:%M:%S'),
                   appointment.time_time.strftime('%Y-%m-%d %H:%M:%S'),
                   u'申请中' if appointment.status == Appointment.STATUS_WAITING else(
                       u'通过' if appointment.status == Appointment.STATUS_PASS else u'未通过'
                   ),
                   appointment.description, appointment.replytext,
                   appointment.score, appointment.comment]
        if appointment.review is not None:
            review = appointment.review
            rowdata.append(review.location)
            rowdata.append(review_type_id2string[review.type])
            rowdata.append(review.message_stu)
            rowdata.append(review.message_men)
            rowdata.append(review.message_slu)
        else:
            rowdata.append(u'')
            rowdata.append(u'')
            rowdata.append(u'')
            rowdata.append(u'')
            rowdata.append(u'')
        data.append(rowdata)

    for row in range(len(data)):
        for col in range(len(data[row])):
            sheet.write(row, col, data[row][col])

    workbook.save(path)


def adminGenerateMentor(mentors, path):
    workbook = xlwt.Workbook(encoding='utf-8')
    sheet = workbook.add_sheet('Appointments')
    data = []
    data.append([u'导师工号', u'导师姓名', u'导师部门', u'评分',
                 u'总预约数', u'通过预约数', u'未通过预约数', u'团体课开课数'])

    for mentor in mentors:
        rowdata = [mentor.id, mentor.name, department_id2name[mentor.department],
                   (mentor.score_all / mentor.score_times) if mentor.score_times > 0 else u'暂无数据']
        apps = mentor.appointments_men
        courses = mentor.courses_men
        num_pass = 0
        num_deny = 0
        for appointment in apps:
            if appointment.status == Appointment.STATUS_PASS:
                num_pass += 1
            elif appointment.status == Appointment.STATUS_DENY:
                num_deny += 1
        rowdata.append(len(apps))
        rowdata.append(num_pass)
        rowdata.append(num_deny)
        rowdata.append(len(courses))
        data.append(rowdata)

    for row in range(len(data)):
        for col in range(len(data[row])):
            sheet.write(row, col, data[row][col])

    workbook.save(path)


def generateWaitingData():
    basedir = os.path.abspath(os.path.dirname(__file__))
    filename = 'static/tmp/data/appointments_waiting_' + datetime.now().strftime('%Y-%m-%d-%H:%M:%S') + '.xls'
    path = os.path.join(basedir, filename)
    print path
    appointments = Appointment.query.filter(Appointment.status == Appointment.STATUS_WAITING).all()
    generateData(appointments, path)
    return path


def generateDailyData():
    basedir = os.path.abspath(os.path.dirname(__file__))
    filename = 'static/tmp/data/appointments_daily_' + datetime.now().strftime('%Y-%m-%d') + '.xls'
    path = os.path.join(basedir, filename)
    appointments = Appointment.query.filter(Appointment.time_submit >= datetime.now().date()).all()
    generateData(appointments, path)
    return path


def generateAllData():
    basedir = os.path.abspath(os.path.dirname(__file__))
    filename = 'static/tmp/data/appointments_all_' + datetime.now().strftime('%Y-%m-%d-%H:%M:%S') + '.xls'
    path = os.path.join(basedir, filename)
    appointments = Appointment.query.all()
    generateData(appointments, path)
    return path


def adminGenerateAppointmentData():
    basedir = os.path.abspath(os.path.dirname(__file__))
    filename = 'static/tmp/data/admin_appointments_' + datetime.now().strftime('%Y-%m-%d-%H:%M:%S') + '.xls'
    path = os.path.join(basedir, filename)
    appointments = Appointment.query.all()
    adminGenerateAppointment(appointments, path)
    return path


def adminGenerateMentorData():
    basedir = os.path.abspath(os.path.dirname(__file__))
    filename = 'static/tmp/data/admin_mentors_' + datetime.now().strftime('%Y-%m-%d-%H:%M:%S') + '.xls'
    path = os.path.join(basedir, filename)
    mentors = User.query.filter(User.identify == User.IDENTIFY_MENTOR).all()
    adminGenerateMentor(mentors, path)
    return path
