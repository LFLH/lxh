#/usertrainregister的后端API
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

# 列表查看系统能力提升培训
@main.route('/searchsystrain')
def searchsystrain():
    trains = Train.query.all()
    result = []
    for train in trains:
        result.append({'name': train.name, 'begintime': train.begintime, 'endtime': train.endtime})
    return jsonify(result)

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

#报名提交能力提升培训
@main.route('/bmsystrain',methods=['GET','POST'])
def bmsystrain():
    return Response(json.dumps({}), mimetype='application/json')