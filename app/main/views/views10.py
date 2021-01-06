"""
    系统活动相关api
"""
import datetime
import json
import os
import time
from flask import request, jsonify, Response

from app import db
from app.main import main
from app.models.models import UDeclare, Activity, Declare, DUDC, User, Train, System, AU, Score


# 添加系统活动
@main.route('/addsysactivity', methods=['GET', 'POST'])
def addsysactivity():
    if request.method == 'GET':
        name = request.args.get('name')
        typeuser = '自主'
        type = request.args.get('type')
        begintime = request.args.get('begintime')
        endtime = request.args.get('endtime')
        stoptime = request.args.get('stoptime')
        main = request.args.get('main')
    else:
        name = request.form.get('name')
        typeuser = '自主'
        type = request.form.get('type')
        begintime = request.form.get('begintime')
        endtime = request.form.get('endtime')
        stoptime = request.form.get('stoptime')
        main = request.form.get('main')
    # username = session.get('username')
    # begintime = datetime.datetime.strptime(begintime, '%Y-%m-%d')
    # endtime = datetime.datetime.strptime(endtime, '%Y-%m-%d')
    # stoptime = stoptime.datetime.strptime(stoptime, '%Y-%m-%d')
    # user = User.query.filter(User.username == username).all()[0]
    userid = 1
    activity = Activity(name=name, begintime=begintime, endtime=endtime, stoptime=stoptime, main=main,
                        type=type, userid=userid)
    db.session.add(activity)
    db.session.commit()
    # user.updatetime = activity.uptime
    # db.session.add(user)
    # db.session.commit()
    # session["activityid"] = activity.id
    return Response(json.dumps({'status': True}), mimetype='application/json')


# 列表查看系统活动
@main.route('/searchsysactivity')
def searchsysactivity():
    result = []
    activities = Activity.query.filter_by(typeuser='xitong').all()
    for activity in activities:
        result.append({'name': activity.name, 'type': activity.type, 'begintime': activity.begintime,
                       'endtime': activity.endtime})
    return jsonify(result)


# 查看系统活动详细信息
@main.route('/detailsysactivitytouse', methods=['GET', 'POST'])
def detailsysactivitytouse():
    if request.method == 'GET':
        name = request.args.get('name')
    else:
        name = request.form.get('name')
    activity = Activity.query.filter_by(name=name).first()
    result = {'name': activity.name, 'typeuser': '系统活动', 'type': activity.type, 'begintime': activity.begintime,
              'endtime': activity.endtime, 'main': activity.main}
    return jsonify(result)


# 系统活动报名
@main.route('/bmsysactivity', methods=['GET', 'POST'])
def bmsysactivity():
    if request.method == 'GET':
        id = request.args.get('id')
    else:
        id = request.form.get('id')
    activityid = id
    # username = session.get('username')
    # user = User.query.filter(User.username == username).first()
    # userid = user.id
    userid = 1
    au = AU(activityid=activityid, userid=userid, type=0, ip='255')
    db.session.add(au)
    db.session.commit()
    return Response(json.dumps({'status': True}), mimetype='application/json')


# 显示系统信息
@main.route('/showsystem')
def showsystem():
    system = System.query.first()
    return jsonify({'类型': system.type, '内容': system.main})


# 显示分数
@main.route('/showscore')
def showscore():
    scores = Score.query.all()
    result = {}
    for score in scores:
        name = User.query.filter_by(id=score.userid).first().username
        if name not in result:
            result.update({name: [{score.year: score.score}]})
        else:
            result[name].append({score.year: score.score})
    return jsonify(result)
