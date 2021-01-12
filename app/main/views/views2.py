#/manage的后端API
from flask import request,jsonify,session,redirect,Response
from app.main import main
from app.models.models import User,Activity,AD,Data,Declare,UDeclare
from app import db
import json,datetime

@main.after_app_request
def after_request(response):
    response.headers['Access-Control-Allow-Origin'] = '*'
    response.headers['Access-Control-Allow-Methods'] = 'PUT,GET,POST,DELETE'
    response.headers['Access-Control-Allow-Headers'] = 'Content-Type,Authorization'
    return response

#获取申报和参与申报的用户数、各月提交数、活动报名人数
@main.route('/manageall')
def manageall():
    activities = Activity.query.all()
    # 所有活动报名的总人数
    activity_users_num = 0
    # 各月提交活动统计
    activity_month = {'1': 0, '2': 0, '3': 0, '4': 0, '5': 0, '6': 0,
                      '7': 0, '8': 0, '9': 0, '10': 0, '11': 0, '12': 0}
    for activity in activities:
        activity_month[str(activity.updatetime.month)] += 1
        for user in activity.users:
            if user.id:
                activity_users_num += 1
    # print(activity_users_num)
    # 申报的任务数
    declare_num = []
    declares = Declare.query.all()
    for declare in declares:
        declare_num.append(declare.id)
    # 申报任务的用户数
    declare_user_num = []
    udclares = UDeclare.query.all()
    for udclare in udclares:
        declare_user_num.append(udclare.userid)
    ud = {"申报任务数": len(set(declare_num)), "参与申报用户数": len(set(declare_user_num))}
    return jsonify(activity_month, ud)