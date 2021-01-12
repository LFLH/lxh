#/manageabilityuser的后端API
from flask import request,jsonify,session,redirect,Response
from app.main import main
from app.models.models import User,Activity,AD,Data,Declare,UDeclare,Train,UTrain
from app import db
import json,datetime

@main.after_app_request
def after_request(response):
    response.headers['Access-Control-Allow-Origin'] = '*'
    response.headers['Access-Control-Allow-Methods'] = 'PUT,GET,POST,DELETE'
    response.headers['Access-Control-Allow-Headers'] = 'Content-Type,Authorization'
    return response

# 列表显示用户申请培训信息
@main.route('/searchabilityuser')
def searchabilityuser():
    # 查询所有的能力提升培训与对应的申请的用户
    result = []
    train = Train.query.all()
    # d:申报任务; ducu:用户申报记录; ud:用户申报;
    for tra in train:
        for t in tra.utrains:
            result.append({'name': User.query.filter_by(id=t.id).first().username, 'begintime': tra.begintime,
                           'endtime': tra.endtime, 'uptime': t.uptime})
    # print(result)
    return jsonify(result)

#显示用户申请培训详细信息
@main.route('/detailabilityuser',methods=['GET','POST'])
def detailabilityuser():
    return Response(json.dumps({}), mimetype='application/json')

#通过用户申请培训
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