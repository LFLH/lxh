#/managedeclareadd的后端API
from flask import request,jsonify,session,redirect,Response
from app.main import main
from app.models.models import User,Activity,AD,Data,Declare,UDeclare
from app import db
import json,datetime
from sqlalchemy import or_,and_

@main.after_app_request
def after_request(response):
    response.headers['Access-Control-Allow-Origin'] = '*'
    response.headers['Access-Control-Allow-Methods'] = 'PUT,GET,POST,DELETE'
    response.headers['Access-Control-Allow-Headers'] = 'Content-Type,Authorization'
    return response

#添加新的申报任务
@main.route('/adddeclare',methods=['GET','POST'])
def adddeclare():
    if request.method == "GET":
        name = request.args.get('name')
        begintime = request.args.get('begintime')
        endtime = request.args.get('endtime')
        main = request.args.get('main')
    else:
        name = request.form.get('name')
        begintime = request.form.get('begintime')
        endtime = request.form.get('endtime')
        main = request.form.get('main')
    begintime = datetime.datetime.strptime(begintime, '%Y-%m-%d')
    endtime = datetime.datetime.strptime(endtime, '%Y-%m-%d')
    #创建申报
    declare=Declare(name=name,begintime=begintime,endtime=endtime,main=main)
    db.session.add(declare)
    db.session.commit()
    #设置新用户提交时间
    user=User.query.filter(and_(User.checked==0,User.type=='user')).all()
    now=str(datetime.datetime.now()).split('-')[0]
    for i in range(len(user)):
        if str(user[i].endtime).split('-')[0]==now:
            user[i].endtime=endtime
            db.session.add(user[i])
            db.session.commit()
    return Response(json.dumps({'status':True}), mimetype='application/json')