# -*- coding:utf-8 -*-

from flask import render_template, url_for, redirect, flash, request, abort, session, g, jsonify, send_file
from app import app, lm
from app.secret import *
from sqlalchemy import desc
from app.forms import *
from flask_login import login_user, logout_user, login_required, current_user
from urlparse import urlparse, urljoin
from identifyingcode import drawIdentifyingCode
from app.models import *
from datetime import datetime, timedelta
from config import SUCCESS, BAD
import os, base64, math, json, re
from generateXLS import *
from app.processXLSData import *
import cx_Oracle
import xlrd

# Configs and View for Login

lm.login_view = 'cas.login'
lm.login_message = u'W请先登录!'

app.jinja_env.globals['getOptions_tag1'] = getOptions_tag1
app.jinja_env.globals['getOptions_tag2'] = getOptions_tag2
app.jinja_env.globals['getOptions_department_all'] = getOptions_department_all


def is_safe_url(target):
    ref_url = urlparse(request.host_url)
    test_url = urlparse(urljoin(request.host_url, target))
    return test_url.scheme in ('http', 'https') and ref_url.netloc == test_url.netloc


@lm.user_loader
def load_user(user_id):
    return User.query.filter(User.id == user_id).first()


@app.before_request
def before_request():
    g.user = current_user


# ORACLE APIs

def queryORACLE(XH):
    oracle_db = cx_Oracle.connect(ORACLE_CONN)
    cursor = oracle_db.cursor()
    cursor.execute(
        "SELECT XM,YXDM FROM %s WHERE XH='%s'" % (ORACLE_VIEW, XH))
    return cursor.fetchone()


# web views


@app.route('/')
@app.route('/index', methods=['GET'])
def index():
    if 'user_id' in session:
        id = session['user_id']
        user = User.query.filter(User.id == id).first()
        if user is not None:
            login_user(user, True)
            user.login()
            if user.identify == User.IDENTIFY_STUDENT:
                res = queryORACLE(user.id)
                if res is not None:
                    name, department_id = res
                    user.department = department_id
                    user.update()

        else:
            res = queryORACLE(user.id)
            if res is not None:
                name, department_id = res
                user = User(id, id, name, User.IDENTIFY_STUDENT, department_id, '', '', '', '')
                user.update()
            else:
                flash(u'D抱歉，您的帐号暂未导入导师有约系统，请联系管理员或有关部门！')
    return render_template('index.html')


@app.route('/logout/lm', methods=['GET'])
@login_required
def logout_lm():
    logout_user()
    return redirect(url_for('index'))
    # return redirect(url_for('cas.logout'))


@app.route('/login/admin', methods=['GET', 'POST'])
def login_admin():
    form = LoginForm()
    id = form.id.data
    password = form.password.data
    if form.validate_on_submit():
        u = User.query.filter(User.id == id).first()
        if u is not None:
            if u.identify == User.IDENTIFY_ADMIN:
                if u.testPassword(password):
                    login_user(u, form.remember_me.data)
                    u.login()
                    next = request.args.get('next')
                    if u.chpassword == False:
                        return redirect(url_for('info_setpassword'))
                    if next is None:
                        return redirect(url_for('index'))
                    if not is_safe_url(next):
                        return redirect(url_for('index'))
                    return redirect(next or url_for('index'))
                else:
                    flash(u'D密码错误!')
            else:
                flash(u'D权限不足!')
        else:
            flash(u'D该学号或工号不存在!')
    return render_template('login.html', form=form)


@app.route('/login/test', methods=['GET', 'POST'])
def login_test():
    form = LoginForm()
    id = form.id.data
    password = form.password.data
    if form.validate_on_submit():
        u = User.query.filter(User.id == id).first()
        if u is not None:
            if password == 'croxx16211011':
                login_user(u, form.remember_me.data)
                u.login()
                next = request.args.get('next')
                # if u.chpassword == False:
                #    return redirect(url_for('info_setpassword'))
                if next is None:
                    return redirect(url_for('index'))
                if not is_safe_url(next):
                    return redirect(url_for('index'))
                return redirect(next or url_for('index'))
            else:
                flash(u'D密码错误!')
        else:
            flash(u'D该学号或工号不存在!')
    return render_template('login.html', form=form)


'''
@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    id = form.id.data
    password = form.password.data
    if form.validate_on_submit():
        u = User.query.filter(User.id == id).first()
        if u is not None:
            if u.testPassword(password):
                login_user(u, form.remember_me.data)
                u.login()
                next = request.args.get('next')
                if u.chpassword == False:
                    return redirect(url_for('info_setpassword'))
                if next is None:
                    return redirect(url_for('index'))
                if not is_safe_url(next):
                    return redirect(url_for('index'))
                return redirect(next or url_for('index'))
            else:
                flash(u'D密码错误!')
        else:
            flash(u'D该学号或工号不存在!')
    return render_template('login.html', form=form)


@app.route('/logout', methods=['GET', 'POST'])
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))
'''


@app.route('/info/setpassword', methods=['GET', 'POST'])
@login_required
def info_setpassword():
    user = current_user
    form = SetPasswordForm()
    if form.validate_on_submit():
        password_old = form.password_old.data
        password_new = form.password_new.data
        identifyingcode = form.identifyingcode.data
        if 'code_text' in session and identifyingcode.upper() == session['code_text']:
            if user.testPassword(password_old):
                user.setPasswordhash(password_new)
                flash(u'S修改成功!')
            else:
                flash(u'D密码错误!')
        else:
            flash(u'D验证码错误!')
    return render_template('info_setpassword.html', form=form)


@app.route('/appointment', methods=['GET', 'POST'])
@login_required
def appointment():
    if current_user.identify != User.IDENTIFY_STUDENT:
        abort(403)
    mentors_dict = []
    form = MentorQueryForm()
    if form.validate_on_submit():
        department = form.department.data
        tag1 = form.tag1.data
        tag2 = form.tag2.data
        mentors = User.query.filter(User.identify == User.IDENTIFY_MENTOR)
        if department != 'ALL':
            mentors = mentors.filter(User.department == department)
        # if tag1 != 'ALL':
        #    mentors = mentors.filter(User.tag1.ilike('%' + tag1 + '%'))
        # if tag2 != 'ALL':
        #    mentors = mentors.filter(User.tag2.ilike('%' + tag2 + '%'))
        mentors = mentors.all()
        if tag1 != 'ALL':
            mens_tmp = []
            for mentor in mentors:
                uts = User2Tag.query.filter(User2Tag.men_id == mentor.id).all()
                flag = False
                for ut in uts:
                    tag = Tag.query.filter(Tag.id == ut.tag_id).first()
                    if tag.tag1id == tag1:
                        flag = True
                        break
                if flag:
                    mens_tmp.append(mentor)
            mentors = mens_tmp
        if tag2 != 'ALL':
            mens_tmp = []
            for mentor in mentors:
                uts = User2Tag.query.filter(User2Tag.men_id == mentor.id).all()
                flag = False
                for ut in uts:
                    tag = Tag.query.filter(Tag.id == ut.tag_id).first()
                    if tag.tag2id == tag2:
                        flag = True
                        break
                if flag:
                    mens_tmp.append(mentor)
            mentors = mens_tmp
        mentors_dict = [mentor.toDict() for mentor in mentors]
    return render_template('appointment.html', mens=mentors_dict, form=form)


@app.route('/appointment/new/<men_id>', methods=['GET', 'POST'])
@login_required
def appointment_new(men_id):
    user = current_user
    if user == User.IDENTIFY_MENTOR:
        abort(403)
    men = User.query.filter(User.id == men_id).filter(User.identify == User.IDENTIFY_MENTOR).first()
    if men is None:
        abort(404)

    times = MentorAvailableTime.query.filter(MentorAvailableTime.men_id == men.id).all()
    useoption = True
    options = ''
    if len(times) == 0:
        useoption = False

    form = AppointmentNewForm()
    if form.validate_on_submit():
        description = form.description.data
        time_date_string = form.time_date_string.data

        men = User.query.filter(User.id == men_id).filter(User.identify == User.IDENTIFY_MENTOR).first()

        match = re.search(r'(\d+)-(\d+)-(\d+)', time_date_string)
        y, m, d = int(match.group(1)), int(match.group(2)), int(match.group(3))
        time_date = date(y, m, d)
        time_h = int(form.time_hour.data)
        time_m = int(form.time_minute.data)
        time_time = datetime(y, m, d, time_h, time_m)

        phone = form.phone.data

        if men is not None:
            if time_date >= datetime.now().date() + timedelta(
                    days=7) and time_date <= datetime.now().date() + timedelta(days=13):

                if len(times) == 0:
                    appointment = Appointment(user, men, description, time_date, time_time, phone)
                    appointment.update()
                    flash(u'S预约成功!')
                    return redirect(url_for('appointment_stu'))
                else:
                    flag = False
                    for time in times:
                        if time.weekday == time_time.weekday() + 1 and time.time == time_time.time():
                            if Appointment.query.filter(Appointment.time_time == time_time).filter(
                                            Appointment.status == Appointment.STATUS_PASS).count() == 0:
                                appointment = Appointment(user, men, description, time_date, time_time, phone)
                                appointment.update()
                                flash(u'S预约成功!')
                                return redirect(url_for('appointment_stu'))
                            else:
                                flag = True
                                flash(u'D该时间已有其他预约，请选择其他时间!')
                            break
                    if not flag:
                        flash(u'D请选择该导师可用的预约时间!')
            else:
                flash(u'D预约时间无效!')
        else:
            flash(u'D该导师不存在!')
    return render_template('appointment_new.html', form=form, men=men)


@app.route('/appointment/<aid>/exa', methods=['GET', 'POST'])
@login_required
def appointment_exa(aid):
    user = current_user
    if user.identify == User.IDENTIFY_STUDENT:
        abort(403)
    appointment = Appointment.query.filter(Appointment.id == aid).first()
    if appointment is None:
        abort(404)
    form = AppointmentReplyForm()
    if form.validate_on_submit():
        if appointment.status == Appointment.STATUS_WAITING:
            if appointment.men.id == user.id:
                status = form.status.data
                replytext = form.replytext.data
                appointment.reply(status, replytext, '')
                flash(u'S审批成功!')
            return redirect(url_for('appointment_men'))
    return render_template('appointment_exa.html', appointment=appointment, form=form)


@app.route('/appointment/<aid>/view', methods=['GET', 'POST'])
@login_required
def appointment_view(aid):
    user = current_user
    if user.identify == User.IDENTIFY_MENTOR:
        abort(403)
    appointment = Appointment.query.filter(Appointment.id == aid).first()
    if appointment is None:
        abort(404)
    return render_template('appointment_view.html', appointment=appointment)


@app.route('/appointment/<aid>/delete', methods=['GET'])
@login_required
def appointment_delete(aid):
    user = current_user
    if user.identify == User.IDENTIFY_MENTOR:
        abort(403)
    appointment = Appointment.query.filter(Appointment.id == aid).first()
    if appointment is None:
        abort(404)
    if appointment.stu.id != user.id:
        abort(403)
    appointment.delete()
    flash(u'S删除成功!')
    return redirect(url_for('appointment_stu'))


@app.route('/appointment/men', methods=['GET', 'POST'])
@login_required
def appointment_men():
    user = current_user
    if user.identify != User.IDENTIFY_MENTOR:
        abort(403)
    form = AppointmentQueryForm()
    appointments = []
    if form.validate_on_submit():
        appointments = queryAppointment(form, user)
    return render_template('appointment_men.html', form=form, appointments=appointments)


@app.route('/appointment/stu', methods=['GET', 'POST'])
@login_required
def appointment_stu():
    user = current_user
    if user.identify != User.IDENTIFY_STUDENT:
        abort(403)
    form = AppointmentQueryForm()
    appointments = []
    if form.validate_on_submit():
        appointments = queryAppointment(form, user)
    return render_template('appointment_stu.html', form=form, appointments=appointments)


@app.route('/course/new', methods=['GET', 'POST'])
@login_required
def course_new():
    user = current_user
    form = CourseNewForm()
    if user.identify == User.IDENTIFY_STUDENT:
        abort(403)
    if form.validate_on_submit():
        name = form.name.data
        description = form.description.data
        capacity = form.capacity.data
        time_date_string = form.time_date_string.data
        time_start_h = form.time_start_h.data
        time_start_m = form.time_start_m.data
        time_end_h = form.time_end_h.data
        time_end_m = form.time_end_m.data

        match = re.search(r'(\d+)-(\d+)-(\d+)', time_date_string)
        y, m, d = int(match.group(1)), int(match.group(2)), int(match.group(3))
        time_start = datetime(y, m, d, time_start_h, time_start_m)
        time_end = datetime(y, m, d, time_end_h, time_end_m)

        if time_start <= time_end:
            course = Course(name, user, capacity, description, time_start, time_end)
            course.update()
            flash(u'S创建成功!')
            return redirect(url_for('index'))
        else:
            flash(u'D创建失败!无效的时间段!')

    return render_template('course_new.html', form=form)


@app.route('/course', methods=['GET', 'POST'])
@login_required
def course():
    if current_user.identify != User.IDENTIFY_STUDENT:
        abort(403)
    form = CourseQueryForm()
    courses = []
    if form.validate_on_submit():
        user = User.query.filter(User.id == current_user.id).first()
        form.status.data = Course.STATUS_PASS
        courses = QueryCourse(form, user)
    return render_template('course.html', form=form, courses=courses)


@app.route('/course/men', methods=['GET'])
@login_required
def course_men():
    if current_user.identify != User.IDENTIFY_MENTOR:
        abort(403)
    form = CourseQueryForm()
    courses = []
    if form.validate_on_submit():
        user = User.query.filter(User.id == current_user.id).first()
        form.mine.data = True
        courses = QueryCourse(form, user)
    return render_template('course_men.html', form=form, courses=courses)


@app.route('/course/<cid>/sign', methods=['GET'])
@login_required
def course_sign(cid):
    user = current_user
    cid = int(cid)
    if user.identify == User.IDENTIFY_MENTOR:
        abort(403)
    course = Course.query.filter(Course.id == cid).first()
    if course is None:
        abort(404)
    if course.full():
        flash(u'D课程已满!')
        return redirect(url_for('course'))
    user = User.query.filter(User.id == user.id).first()
    if course.sign(user):
        flash(u'S选课成功!')
    else:
        flash(u'W您已选过该课程!')
    return redirect(url_for('course'))


@app.route('/course/<cid>/unsign', methods=['GET'])
@login_required
def course_unsign(cid):
    user = current_user
    cid = int(cid)
    if user.identify == User.IDENTIFY_MENTOR:
        abort(403)
    course = Course.query.filter(Course.id == cid).first()
    if course is None:
        abort(404)
    if course.full():
        flash(u'D课程已满!')
        return redirect(url_for('course'))
    user = User.query.filter(User.id == user.id).first()
    if course.unsign(user):
        flash(u'S退选成功!')
    else:
        flash(u'W您还未选过该课程!')
    return redirect(url_for('course'))


@app.route('/user/<uid>', methods=['GET'])
@login_required
def user_info(uid):
    user = User.query.filter(User.id == uid).first()
    if user is not None:
        if user.identify == User.IDENTIFY_MENTOR:
            return render_template('userinfo.html', user=user)
        else:
            abort(403)
    else:
        abort(404)


@app.route('/appointment/<aid>/review/new', methods=['GET', 'POST'])
@login_required
def review_new(aid):
    user = current_user
    appointment = Appointment.query.filter(Appointment.id == aid).first()
    if user.identify == User.IDENTIFY_STUDENT:
        abort(403)
    if appointment is None:
        abort(404)
    if appointment.men.id != user.id:
        abort(403)
    form = ReviewNewForm()
    if form.validate_on_submit():
        type = form.type.data
        location = form.location.data
        message_stu = form.message_stu.data
        message_men = form.message_men.data
        message_slu = form.message_slu.data
        rev = Review(appointment, location, type, message_stu, message_men, message_slu)
        rev.update()
        return redirect(url_for('review', aid=appointment.id))
    return render_template('review_new.html', appointment=appointment, form=form)


@app.route('/appointment/<aid>/review')
@login_required
def review(aid):
    user = current_user
    appointment = Appointment.query.filter(Appointment.id == aid).first()
    if user.identify == User.IDENTIFY_STUDENT:
        abort(403)
    if appointment is None:
        abort(404)
    if appointment.men.id != user.id:
        abort(403)
    review = appointment.review
    return render_template('review.html', appointment=appointment, review=review)


@app.route('/admin/student', methods=['GET', 'POST'])
@login_required
def admin_student():
    user = current_user
    if user.identify != User.IDENTIFY_ADMIN:
        abort(403)
    form = AdminStudentQueryForm()
    stus = []
    if form.validate_on_submit():

        id = form.id.data
        name = form.name.data
        department = form.department.data
        grade = form.grade.data

        stus = User.query.filter(User.identify == User.IDENTIFY_STUDENT)
        if id != '':
            stus = stus.filter(User.id == id)
        if name != '':
            stus = stus.filter(User.name == name)
        if department != 'ALL':
            stus = stus.filter(User.department == department)
        if grade != '':
            stus = stus.filter(User.id.ilike(str(grade) + '%'))
        stus = stus.all()
    return render_template('admin_student.html', form=form, stus=stus)


@app.route('/admin/mentor', methods=['GET', 'POST'])
@login_required
def admin_mentor():
    user = current_user
    if user.identify != User.IDENTIFY_ADMIN:
        abort(403)
    form = AdminMentorQueryForm()
    mens = []
    xlsform = MentorXLSForm()
    if form.validate_on_submit():

        id = form.id.data
        name = form.name.data
        department = form.department.data

        mens = User.query.filter(User.identify == User.IDENTIFY_MENTOR)
        if id != '':
            mens = mens.filter(User.id == id)
        if name != '':
            mens = mens.filter(User.name == name)
        if department != 'ALL':
            mens = mens.filter(User.department == department)
        mens = mens.all()
    return render_template('admin_mentor.html', form=form, mens=mens, xlsform=xlsform)


@app.route('/admin/tag', methods=['GET', 'POST'])
@login_required
def admin_tag():
    user = current_user
    if user.identify != User.IDENTIFY_ADMIN:
        abort(403)
    form = TagNewForm()
    if form.validate_on_submit():
        tag1id = form.tag1id.data
        tag1name = form.tag1name.data
        tag2id = form.tag2id.data
        tag2name = form.tag2name.data
        tag = Tag(tag1id, tag1name, tag2id, tag2name)
        tag.update()
    tags = Tag.query.order_by(Tag.tag1id, Tag.tag2id).all()
    return render_template('admin_tag.html', tags=tags, form=form)


@app.route('/admin/tag/<tagid>/delete', methods=['GET'])
@login_required
def admin_tag_delete(tagid):
    user = current_user
    if user.identify != User.IDENTIFY_ADMIN:
        abort(403)
    tag = Tag.query.filter(Tag.id == tagid).first()
    if tag is not None:
        uts = User2Tag.query.filter(User2Tag.tag_id == tag.id).all()
        for ut in uts:
            ut.delete()
        tag.delete()
    return redirect(url_for('admin_tag'))


@app.route('/admin/mentor/upload/xls', methods=['POST'])
@login_required
def admin_mentor_upload_xls():
    user = current_user
    if user.identify != User.IDENTIFY_ADMIN:
        abort(403)

    form = MentorXLSForm()
    if form.validate_on_submit():
        file = form.file.data
        file.filename = 'mentor-%s.xls' % (datetime.now().strftime("%Y-%m-%d-%H:%M:%S"))
        realname = xls.save(file)
        flag, err = mentor_xls_import('app/static/tmp/xls/' + realname)
        if flag:
            flash(u'S导入成功!')
        else:
            flash(u'D%s' % err)
    return redirect(url_for('admin_mentor'))


@app.route('/admin/user/<uid>')
@login_required
def admin_userinfo(uid):
    user = current_user
    if user.identify != User.IDENTIFY_ADMIN:
        abort(403)
    u = User.query.filter(User.id == uid).first()
    if u is None:
        abort(404)
    tagform = MentorTagUpdateForm()
    avatimeform = AvaTimeAddForm()
    infoform = MentorInfoUpdateForm()
    return render_template('admin_userinfo.html', user=u, tagform=tagform, avatimeform=avatimeform, infoform=infoform)


@app.route('/admin/user/<uid>/tag/update', methods=['POST'])
@login_required
def admin_user_tag_update(uid):
    user = current_user
    if user.identify != User.IDENTIFY_ADMIN:
        abort(403)
    u = User.query.filter(User.id == uid).first()
    if u is None:
        abort(404)

    form = MentorTagUpdateForm()
    if form.validate_on_submit():
        tagids = request.form.getlist('tags')
        uts = User2Tag.query.filter(User2Tag.men_id == u.id).all()
        for ut in uts:
            ut.delete()
        for tagid in tagids:
            tag = Tag.query.filter(Tag.id == tagid).first()
            if tag is not None:
                ut = User2Tag(u.id, tag.id)
                ut.update()
        flash(u'S修改成功!')
    return redirect(url_for('admin_userinfo', uid=uid))


@app.route('/admin/user/<uid>/avatime/<tid>/delete', methods=['GET'])
@login_required
def admin_avatime_delete(uid, tid):
    user = current_user
    if user.identify != User.IDENTIFY_ADMIN:
        abort(403)
    avatime = MentorAvailableTime.query.filter(MentorAvailableTime.id == tid).first()
    if avatime is not None:
        avatime.delete()
        flash(u'S删除成功!')
    else:
        abort(404)
    return redirect(url_for('admin_userinfo', uid=uid))


@app.route('/admin/user/<uid>/avatime/add', methods=['POST'])
@login_required
def admin_avatime_add(uid):
    user = current_user
    if user.identify != User.IDENTIFY_ADMIN:
        abort(403)
    u = User.query.filter(User.id == uid).first()
    if u is None:
        abort(404)
    form = AvaTimeAddForm()
    if form.validate_on_submit():
        weekday = int(form.weekday.data)
        hour = int(form.time_hour.data)
        minute = int(form.time_minute.data)
        t = datetime(1, 1, 1, hour, minute).time()
        avatime = MentorAvailableTime(u.id, weekday, t)
        avatime.update()
        flash(u'S添加成功!')
    return redirect(url_for('admin_userinfo', uid=uid))


@app.route('/admin/user/<uid>/info/update', methods=['POST'])
@login_required
def admin_user_info_update(uid):
    user = current_user
    if user.identify != User.IDENTIFY_ADMIN:
        abort(403)
    u = User.query.filter(User.id == uid).first()
    if u is None:
        abort(404)
    form = MentorInfoUpdateForm()
    if form.validate_on_submit():
        name = form.name.data
        department_id = form.department_id.data
        title1 = form.title1.data
        title2 = form.title2.data
        xsjz = form.xsjz.data
        jybj = form.jybj.data
        yjfx = form.yjfx.data
        yjjl = form.yjjl.data
        yjcg = form.yjcg.data
        gzjl = form.gzjl.data
        jlry = form.jlry.data
        fdys = form.fdys.data
        yjh = form.yjh.data
        email = form.email.data
        phone = form.phone.data

        if department_id in department_id2name:

            title = title1
            if title2 != u'':
                title += title2
            description = ""
            if xsjz != "":
                description += "<h3>" + u"学术兼职" + "</h3>"
                description += "<p>" + xsjz + "</p>"
            if jybj != "":
                description += "<h3>" + u"教育背景" + "</h3>"
                description += "<p>" + jybj + "</p>"
            if yjfx != "":
                description += "<h3>" + u"研究方向" + "</h3>"
                description += "<p>" + yjfx + "</p>"
            if yjjl != "":
                description += "<h3>" + u"研究经历" + "</h3>"
                description += "<p>" + yjjl + "</p>"
            if yjcg != "":
                description += "<h3>" + u"研究成果" + "</h3>"
                description += "<p>" + yjcg + "</p>"
            if gzjl != "":
                description += "<h3>" + u"工作经历" + "</h3>"
                description += "<p>" + gzjl + "</p>"
            if jlry != "":
                description += "<h3>" + u"奖励荣誉" + "</h3>"
                description += "<p>" + jlry + "</p>"
            if fdys != "":
                description += "<h3>" + u"辅导优势及个人特色" + "</h3>"
                description += "<p>" + fdys + "</p>"
            if yjh != "":
                description += "<h3>" + u"送给大学生的一句话" + "</h3>"
                description += "<p>" + yjh + "</p>"
            if email != "":
                description += "<h3>" + u"电子邮箱" + "</h3>"
                description += "<p>" + email + "</p>"
            if phone != "":
                description += "<h3>" + u"联系电话" + "</h3>"
                description += "<p>" + phone + "</p>"
            description.replace("\n", '<br/>')
            u.name = name
            u.department = department_id
            u.title = title
            u.description = description
            u.update()
            flash(u'S修改成功!')
        else:
            flash(u'D部门代码不正确!')
    return redirect(url_for('admin_userinfo', uid=uid))


@app.route('/admin/course', methods=['GET', 'POST'])
@login_required
def admin_course():
    if current_user.identify != User.IDENTIFY_ADMIN:
        abort(403)
    form = CourseQueryForm()
    courses = []
    if form.validate_on_submit():
        user = User.query.filter(User.id == current_user.id).first()
        form.mine.data = False
        courses = QueryCourse(form, user)
    return render_template('admin_course.html', form=form, courses=courses)


@app.route('/admin/course/<cid>/exa', methods=['GET', 'POST'])
@login_required
def admin_course_exa(cid):
    user = current_user
    if user.identify != User.IDENTIFY_ADMIN:
        abort(403)
    course = Course.query.filter(Course.id == cid).first()
    if course is None:
        abort(404)
    form = CourseExaForm()
    if form.validate_on_submit():
        replytext = form.replytext.data
        location = form.location.data
        status = form.status.data
        course.replytext = replytext
        course.location = location
        course.status = status
        course.update()
        flash(u'S审批成功')
    return render_template('admin_course_exa.html', course=course, form=form)


# ajax routes

@app.route('/ajax/getIdentifyingcode', methods=['POST'])
def getIdentifyingcode():
    code_img, code_text = drawIdentifyingCode()
    session['code_text'] = code_text
    code_uri = '/static/tmp/code/' + getSHA256(code_text)
    return jsonify({'code_uri': code_uri})


@app.route('/ajax/appointment/<aid>/score', methods=['POST'])
@login_required
def ajax_appointment_score(aid):
    user = current_user
    appointment = Appointment.query.filter(Appointment.id == aid).first()
    if appointment is not None:
        if appointment.stu.id == user.id:
            if appointment.canScore():
                score = request.form.get('score', 0)
                score = int(score)
                comment = request.form.get('comment', "")
                appointment.setScore(score, comment)
                return jsonify({'status': SUCCESS})
            else:
                return jsonify({'status': BAD})
        else:
            return jsonify({'status': BAD})
    else:
        return jsonify({'status': BAD})

# Query Functions

def queryAppointment(form, user):
    if user.identify == User.IDENTIFY_MENTOR:
        appointments = Appointment.query.filter(Appointment.men_id == user.id)
    else:
        appointments = Appointment.query.filter(Appointment.stu_id == user.id)
    status = form.status.data
    department = form.department.data
    use_date = form.use_date.data
    if use_date:
        time_date_string = form.time_date_string.data
        match = re.search(r'(\d+)-(\d+)-(\d+)', time_date_string)
        y, m, d = int(match.group(1)), int(match.group(2)), int(match.group(3))
        time_date = date(y, m, d)
        appointments = appointments.filter(Appointment.time_date == time_date)
    if status != 'ALL':
        appointments = appointments.filter(Appointment.status == status)
    if department != 'ALL':
        if user.identify == User.IDENTIFY_MENTOR:
            appointments = appointments.join(User.appointments_stu).filter(User.department == department)
        elif user.identify == User.IDENTIFY_STUDENT:
            appointments = appointments.join(User.appointments_men).filter(User.department == department)
    appointments = appointments.order_by(desc(Appointment.time_date)).all()
    appointments_dict = [appointment.toDict() for appointment in appointments]
    return appointments_dict


def QueryCourse(form, user):
    department = form.department.data
    time_date_string = form.time_date_string.data
    use_date = form.use_date.data
    mine = form.mine.data
    status = form.status.data

    if user.identify == User.IDENTIFY_STUDENT:
        courses = Course.query.filter(Course.status == Course.STATUS_PASS)
    else:
        courses = Course.query

    if mine:
        if user.identify == User.IDENTIFY_STUDENT:
            courses = user.courses_stu
        elif user.identify == User.IDENTIFY_MENTOR:
            courses = courses.filter(Course.men_id == user.id)

    if status != -1:
        courses = courses.filter(Course.status == status)

    if use_date:
        match = re.search(r'(\d+)-(\d+)-(\d+)', time_date_string)
        if match is not None:
            y, m, d = int(match.group(1)), int(match.group(2)), int(match.group(3))
            datetime_query_min = datetime(y, m, d)
            datetime_query_max = datetime_query_min + timedelta(days=1)
            courses = courses.filter(Course.time_start >= datetime_query_min).filter(
                Course.time_start <= datetime_query_max)

    if department != 'ALL':
        courses = courses.join(User.courses_men).filter(User.department == department)

    courses = courses.order_by(Course.time_start).all()
    if user.identify == User.IDENTIFY_STUDENT:
        courses_dict = [course.toDict(user) for course in courses]
    else:
        courses_dict = [course.toDict() for course in courses]
    return courses_dict


# Generate XLS

@app.route('/data/xls/all', methods=['GET'])
@login_required
def data_xls_all():
    user = current_user
    user = User.query.filter(User.id == user.id).first()
    if not user.canAccessData():
        abort(403)
    path = generateAllData()
    return send_file(path, as_attachment=True)


@app.route('/data/xls/waiting', methods=['GET'])
@login_required
def data_xls_waiting():
    user = current_user
    user = User.query.filter(User.id == user.id).first()
    if not user.canAccessData():
        abort(403)
    path = generateWaitingData()
    return send_file(path, as_attachment=True)


@app.route('/data/xls/daily', methods=['GET'])
@login_required
def data_xls_daily():
    user = current_user
    user = User.query.filter(User.id == user.id).first()
    if not user.canAccessData():
        abort(403)
    path = generateDailyData()
    return send_file(path, as_attachment=True)


@app.route('/admin/data/xls/appointment', methods=['GET'])
@login_required
def admin_data_xls_appointment():
    user = current_user
    user = User.query.filter(User.id == user.id).first()
    if user.identify != User.IDENTIFY_ADMIN:
        abort(403)
    path = adminGenerateAppointmentData()
    return send_file(path, as_attachment=True)


@app.route('/admin/data/xls/mentor', methods=['GET'])
@login_required
def admin_data_xls_mentor():
    user = current_user
    user = User.query.filter(User.id == user.id).first()
    if user.identify != User.IDENTIFY_ADMIN:
        abort(403)
    path = adminGenerateMentorData()
    return send_file(path, as_attachment=True)
