# -*- coding:utf-8 -*-
from app.models import *
import xlrd


def mentor_xls_validate(path):
    data = xlrd.open_workbook(path)
    if len(data.sheets()) != 3:
        return False, u'文件表格数不正确!\n'
    flag = True
    err = ''
    sheet = data.sheets()[0]
    for i in range(1, sheet.nrows):
        row = sheet.row_values(i)
        department_id = str(row[2])
        if department_id not in department_id2name:
            flag = False
            err += u'表1第%s行部门代码不存在!\n' % i + 1
    sheet = data.sheets()[1]
    for i in range(1, sheet.nrows):
        row = sheet.row_values(i)
        t = str(row[1])
        m = re.search(ur'\d+', t)
        if m is None:
            flag = False
            err += u'表2第%s行星期格式不正确!\n' % i + 1
        else:
            m = m.group()
            m = int(m)
            if not (m >= 1 and m <= 7):
                flag = False
                err += u'表2第%s行星期不正确!\n' % i + 1
        t = str(row[2])
        m = re.search(ur'\d+:\d+', t)
        if m is None:
            flag = False
            err += u'表2第%s行时间格式不正确!\n' % i + 1
    sheet = data.sheets()[2]
    for i in range(1, sheet.nrows):
        row = sheet.row_values(i)
        tag2 = str(row[1])
        tag = Tag.query.filter(Tag.tag2id == tag2).first()
        if tag is None:
            flag = False
            err += u'表3第%s行细分标签不存在，请先添加标签!\n' % i + 1
    return flag, err


def mentor_xls_import(path):
    flag, err = mentor_xls_validate(path)
    if not flag:
        return flag, err
    data = xlrd.open_workbook(path)
    sheet = data.sheets()[0]
    for i in range(1, sheet.nrows):
        row = sheet.row_values(i)
        id = str(row[0])
        department = str(row[2])
        name = row[1]
        title = row[3]
        if row[4] != "":
            title += ',' + row[4]

        description = ""
        if row[5] != "":
            description += "<h3>" + u"学术兼职" + "</h3>"
            description += "<p>" + str(row[5]) + "</p>"
        if row[6] != "":
            description += "<h3>" + u"教育背景" + "</h3>"
            description += "<p>" + str(row[6]) + "</p>"
        if row[7] != "":
            description += "<h3>" + u"研究方向" + "</h3>"
            description += "<p>" + str(row[7]) + "</p>"
        if row[8] != "":
            description += "<h3>" + u"研究经历" + "</h3>"
            description += "<p>" + str(row[8]) + "</p>"
        if row[9] != "":
            description += "<h3>" + u"研究成果" + "</h3>"
            description += "<p>" + str(row[9]) + "</p>"
        if row[10] != "":
            description += "<h3>" + u"工作经历" + "</h3>"
            description += "<p>" + str(row[10]) + "</p>"
        if row[11] != "":
            description += "<h3>" + u"奖励荣誉" + "</h3>"
            description += "<p>" + str(row[11]) + "</p>"
        if row[12] != "":
            description += "<h3>" + u"辅导优势及个人特色" + "</h3>"
            description += "<p>" + str(row[12]) + "</p>"
        if row[13] != "":
            description += "<h3>" + u"送给大学生的一句话" + "</h3>"
            description += "<p>" + str(row[13]) + "</p>"
        if row[14] != "":
            description += "<h3>" + u"电子邮箱" + "</h3>"
            description += "<p>" + str(row[14]) + "</p>"
        if row[15] != "":
            description += "<h3>" + u"联系电话" + "</h3>"
            description += "<p>" + str(row[15]) + "</p>"
        description.replace("\n", '<br/>')

        user = User.query.filter(User.identify == User.IDENTIFY_MENTOR).filter(User.id == id).first()
        if user is None:
            user = User(id, id + '123456', name, User.IDENTIFY_MENTOR, department, '', '', title, description)
            user.update()
        else:
            user.name = name
            user.department = department
            user.titie = title
            user.description = description
            user.update()

    sheet = data.sheets()[1]
    for i in range(1, sheet.nrows):
        row = sheet.row_values(i)
        id = row[0]
        w = row[1]
        w = int(w)
        h, m = re.search(ur'(\d+):(\d+)', str(row[2])).group(1, 2)
        h, m = int(h), int(m)
        ma = MentorAvailableTime(id, w, datetime(1, 1, 1, h, m).time())
        ma.update()

    sheet = data.sheets()[2]
    for i in range(1, sheet.nrows):
        row = sheet.row_values(i)
        id = row[0]
        tag2 = row[1]
        tag = Tag.query.filter(Tag.tag2id == tag2).first()
        ut = User2Tag(id, tag.id)
        ut.update()
    return True, ''
