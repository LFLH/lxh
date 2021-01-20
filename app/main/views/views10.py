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
    system = System.query.first()
    return Response(json.dumps({'type': system.type, 'main': system.main}), mimetype='application/json')

#修改系统信息
@main.route('/updatesystem',methods=['GET','POST'])
def updatesystem():
    if request.method == "GET":
        type = request.args.get('type')
        main=request.args.get('main')
    else:
        type = request.json.get('type')
        main = request.json.get('main')
    #修改系统信息
    system=System.query.filter(System.type==type).all()[0]
    system.main=main
    db.session.add(system)
    db.session.commit()
    return Response(json.dumps({'status': True}), mimetype='application/json')