# -*- coding:utf-8 -*-

import xlwt
from app.models import *

appointments = Appointment.query.all()

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
               appointment.description,appointment.replytext]
    data.append(rowdata)

for row in range(len(data)):
    for col in range(len(data[row])):
        sheet.write(row,col,data[row][col])

workbook.save('data.xls')

'''
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


'''
