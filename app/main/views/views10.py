#/managesystem的后端API
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

# 显示系统信息
@main.route('/showsystem',methods=['GET','POST'])
def showsystem():
    type = System.query.with_entities(System.type).distinct().all()
    data=[]
    for systype in type:
        system=System.query.filter(System.type==systype[0]).all()
        if len(system)==1:
            sys={'type':systype[0],'main':system[0].main}
        else:
            main = []
            for i in range(len(system)):
                main.append(system[i].main)
            sys={'type':systype[0],'main':main}
        data.append(sys)
    return Response(json.dumps({'data':data}), mimetype='application/json')

#修改系统信息
@main.route('/updatesystem',methods=['GET','POST'])
def updatesystem():
    if request.method == "GET":
        type = request.args.get('type')
        main=request.args.get('main')
    else:
        #type = request.json.get('type')
        #main = request.json.get('main')
        type = request.form.get('type')
        main = request.form.get('main')
    #修改系统信息
    system=System.query.filter(System.type==type).all()[0]
    if main!=None:
        system.main=main
    db.session.add(system)
    db.session.commit()
    return Response(json.dumps({'status': True}), mimetype='application/json')

#添加系统设置
@main.route('/addsystem',methods=['GET','POST'])
def addsystem():
    if request.method == "GET":
        type = request.args.get('type')
        main=request.args.get('main')
    else:
        #type = request.json.get('type')
        #main = request.json.get('main')
        type = request.form.get('type')
        main = request.form.get('main')
    system=System(type=type,main=main)
    db.session.add(system)
    db.session.commit()
    return Response(json.dumps({'status': True}), mimetype='application/json')

#获取活动类型
@main.route('/getactivitytype',methods=['GET','POST'])
def getactivitytype():
    system = System.query.filter(System.type == 'activitytype').all()
    main = []
    for i in range(len(system)):
        main.append(system[i].main)
    return Response(json.dumps({'data': main}), mimetype='application/json')