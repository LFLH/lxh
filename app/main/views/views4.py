#/managedeclareuser的后端API
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

#列表显示用户申报信息
@main.route('/searchdeclareuser')
def searchdeclareuser():
    # 查询所有的申报任务与对应的申报用户
    result = []
    declare = Declare.query.all()
    # declare.udeclares返回UDeclare的列表
    # d:申报任务; ducu:用户申报记录; ud:用户申报;
    for dec in declare:
        for d in dec.udeclares:
            result.append({'name': User.query.filter_by(id=d.id).first().username, 'begintime': dec.begintime,
                           'endtime': dec.endtime, 'uptime': d.uptime})
    # print(result)
    return jsonify(result)

#显示用户申报的详细信息
@main.route('/detaildeclareuser',methods=['GET','POST'])
def detaildeclareuser():
    return Response(json.dumps({}), mimetype='application/json')

#通过用户申报
@main.route('/tgdeclareuser', methods=['GET', 'POST'])
def tgdeclareuser():
    if request.method == 'GET':
        id = request.args.get('id')
    else:
        id = request.form.get('id')
    udeclare = UDeclare.query.filter_by(id=id).first()
    udeclare.type = 1
    db.session.commit()
    return Response(json.dumps({'status': True}), mimetype='application/json')