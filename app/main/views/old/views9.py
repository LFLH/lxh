"""
    能力提升相关api
"""
import datetime
import json
import os
import time
from flask import request, jsonify, Response

from app import db
from app.main import main
from app.models.models import UDeclare, Activity, Declare, DUDC, User, Train, UTrain


# 添加新的能力提升培训
@main.route('/addability', methods=['GET', 'POST'])
def addability():
    if request.method == 'GET':
        name = request.args.get('name')
        begintime = request.args.get('begintime')
        endtime = request.args.get('endtime')
        main = request.args.get('main')
    else:
        name = request.form.get('name')
        begintime = request.form.get('begintime')
        endtime = request.form.get('endtime')
        main = request.form.get('main')
    userid = 1
    uptime = datetime.datetime.now()
    utrain = UTrain(userid=userid, uptime=uptime)
    train = Train(name=name, begintime=begintime, endtime=endtime, main=main)

    db.session.add(train)
    db.session.commit()
    return Response(json.dumps({'status': True}), mimetype='application/json')


# 列表查看系统能力提升培训
@main.route('/searchsystrain')
def searchsystrain():
    trains = Train.query.all()
    result = []
    for train in trains:
        result.append({'name': train.name, 'begintime': train.begintime, 'endtime': train.endtime})
    return jsonify(result)


# 通过用户申请培训
@main.route('/tgabilityuser', methods=['GET', 'POST'])
def tgabilityuser():
    if request.method == 'GET':
        id = request.args.get('id')
    else:
        id = request.form.get('id')
    utrain = UTrain.query.filter_by(id=id).first()
    utrain.type = 1
    db.session.commit()
    return Response(json.dumps({'status': True}), mimetype='application/json')


# 查看系统能力提升培训详细信息
@main.route('/detailsystrain', methods=['GET', 'POST'])
def detailsystrain():
    if request.method == 'GET':
        name = request.args.get('name')
    else:
        name = request.form.get('name')
    train = Train.query.filter_by(name=name).first()
    result = {'name': train.name, 'main': train.main, 'begintime': train.begintime, 'endtime': train.endtime}
    return jsonify(result)