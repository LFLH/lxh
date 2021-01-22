#/useractivitysign/<activityid>的后端API
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

#系统报名用户获取
@main.route('/signuserz',methods=['GET','POST'])
def signuserz():
    if request.method == "GET":
        activityid = request.args.get('activityid')#活动id
    else:
        activityid = request.json.get('activityid')
    # 获取系统活动的报名用户
    userz = User.query.join(AU).join(Activity).filter(Activity.id == activityid).all()
    user = []
    for users in userz:
        user.append({"id": users.id, "username": users.username})
    return Response(json.dumps({'userz':user}), mimetype='application/json')

#系统活动签到
@main.route('/signuseractivity',methods=['GET','POST'])
def signuseractivity():
    if request.method == "GET":
        activityid = request.args.get('activityid')#活动id
        userid=request.args.get('userid')#单位id
    else:
        activityid = request.json.get('activityid')
        userid = request.json.get('userid')
    #获取客户端ip地址
    ip=request.remote_addr
    #检查是否同一个ip签到两次
    aui=AU.query.filter(and_(AU.activityid==activityid,AU.ip==ip)).all()
    #签到两次，修改单位id号
    if len(aui)>0:
        aus=aui[0]
        aus.userid=userid
    #初次签到，修改状态，记录ip地址
    else:
        aus=AU.query.filter(and_(AU.activityid==activityid,AU.userid==userid)).all()[0]
        aus.type=1
        aus.ip=ip
    db.session.add(aus)
    db.session.commit()
    return Response(json.dumps({'status':True}), mimetype='application/json')