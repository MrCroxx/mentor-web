# -*- coding:utf-8
from app.models import *
import xlrd

data = xlrd.open_workbook('data/stus.xlsx')

sheet = data.sheets()[0]

nrows = sheet.nrows

for i in range(1, nrows):
    row = sheet.row_values(i)
    id, name, department, year = row[0], row[1], row[2], row[3]
    print id, name, department
    user = User(id, id, name, User.IDENTIFY_STUDENT, department, '', '', '', '')
    user.update()
    # user = User(id, id, name, User.IDENTIFY_STUDENT, department, '', '')
    # user.update()
