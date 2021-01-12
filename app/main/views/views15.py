#/useractivityregister的后端API
from flask import request,jsonify,session,redirect,Response
from app.main import main
from app.models.models import User,Activity,AD,Data,Declare,UDeclare,Train,UTrain,Score,System,AU
from app import db
import json,datetime,random,string,os
from sqlalchemy import or_,and_
from werkzeug.utils import secure_filename

@main.after_app_request
def after_request(response):
    response.headers['Access-Control-Allow-Origin'] = '*'
    response.headers['Access-Control-Allow-Methods'] = 'PUT,GET,POST,DELETE'
    response.headers['Access-Control-Allow-Headers'] = 'Content-Type,Authorization'
    return response

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
@main.route('/detailsysactivitytouser', methods=['GET', 'POST'])
def detailsysactivitytouser():
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