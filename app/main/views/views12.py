#/olduser的后端API
from flask import request,jsonify,session,redirect,Response
from app.main import main
from app.models.models import User,Activity,AD,Data,Declare,UDeclare,Train,UTrain,Score,System
from app import db
import json,datetime,random,string
from sqlalchemy import or_,and_

@main.after_app_request
def after_request(response):
    response.headers['Access-Control-Allow-Origin'] = '*'
    response.headers['Access-Control-Allow-Methods'] = 'PUT,GET,POST,DELETE'
    response.headers['Access-Control-Allow-Headers'] = 'Content-Type,Authorization'
    return response

# 获取用户提交活动数、系统要求参与数、各月提交数、活动状态、培训申请状态
@main.route('/olduserall')
def olduserall():
    # 统计用户提交的活动数量
    # username = session.get('username')
    # userid = User.query.filter_by(username=username).first().id
    userid = 1
    activities = Activity.query.filter_by(userid=userid).all()
    user_activity_num = len(activities)
    # 总任务数量
    # 各月提交活动统计
    activity_month = {'1': 0, '2': 0, '3': 0, '4': 0, '5': 0, '6': 0,
                      '7': 0, '8': 0, '9': 0, '10': 0, '11': 0, '12': 0}
    # 统计活动状态
    activity_status = {}
    for activity in activities:
        activity_month[str(activity.updatetime.month)] += 1
        activity_status.update({activity.name: activity.status})

    # 培训申请状态 根据用户，找到对应的utrain，再找到对应的train, utrain-train一对一
    user = User.query.filter_by(id=userid).first()
    # user.userut：用户提交的用户申请培训表
    train_type = {}
    for ut in user.userut:
        train_type.update({ut.tuts.first().name: ut.type})

    # 活动申请状态
    activity_status = {}
    for activity in activities:
        activity_status.update({activity.name: activity.status})
    return jsonify(activity_month, activity_status, train_type, activity_status)