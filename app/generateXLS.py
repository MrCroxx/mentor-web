# -*- coding:utf-8 -*-

import xlwt
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


def generateWaitingData():
    path = 'appointments_waiting_' + datetime.now().strftime('%Y-%m-%d %H:%M:%S') + '.xls'
    appointments = Appointment.query.filter(Appointment.status == Appointment.STATUS_WAITING).all()
    generateData(appointments, path)
    return path


def generateTodayData():
    path = 'data_' + datetime.now().strftime('%Y-%m-%d') + '.xls'
    appointments = Appointment.query.filter(Appointment.time_submit >= datetime.now().date()).all()
    generateData(appointments, path)
    return path

def generateAllData():
    path = 'data_all_'+ datetime.now().strftime('%Y-%m-%d %H:%M:%S') + '.xls'
    appointments = Appointment.query.all()
    generateData(appointments, path)
    return path
