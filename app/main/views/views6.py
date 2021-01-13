#/manageabilityuser的后端API
from flask import request,jsonify,session,redirect,Response
from app.main import main
from app.models.models import User,Activity,AD,Data,Declare,UDeclare,Train,UTrain,TUT
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
    if request.method == "GET":
        page = request.args.get('page')#当前页
        per_page=request.args.get('per_page')#平均页数
    else:
        page = request.json.get('page')
        per_page = request.json.get('per_page')
    page = int(page)
    per_page = int(per_page)
    # 连表查询未过期的用户申请培训
    utrain=UTrain.query.join(TUT).join(Train).filter(Train.endtime>datetime.datetime.now()).order_by(-UTrain.uptime).paginate(page, per_page, error_out=False)
    items = utrain.items
    item = []
    count = (int(page) - 1) * int(per_page)
    for i in range(len(items)):
        # 获取用户名
        username = User.query.filter_by(id=items[i].userid).all()[0].username
        # 获取对应的培训任务
        train = Train.query.join(TUT).join(UTrain).filter(UTrain.id == items[i].id).all()[0]
        # 用户申请状态
        if items[i].type == 1:
            status = 1
        elif train.endtime < datetime.datetime.now():
            status = 1
        else:
            status = 0
        # 返回id，用户名，培训名，培训起始时间，结束时间，提交时间，能否点击通过按钮的状态
        itemss = {'number': count + i + 1, 'id': items[i].id, 'username': username,'name':train.name,'begintime': str(train.begintime),
                  'endtime': str(train.endtime), 'uptime': str(items[i].uptime),'status':status}
        item.append(itemss)
    # 返回总页数、活动总数、当前页、用户申报集合
    data = {'zpage': utrain.pages, 'total': utrain.total, 'dpage': utrain.page, 'item': item}
    return Response(json.dumps(data), mimetype='application/json')


#显示用户申请培训详细信息
@main.route('/detailabilityuser',methods=['GET','POST'])
def detailabilityuser():
    if request.method == 'GET':
        id = request.args.get('id')
    else:
        id = request.form.get('id')
    # 获取用户申请培训
    utrain=UTrain.query.filter(UTrain.id==id).all()[0]
    # 获取用户名
    name = User.query.filter_by(id=utrain.userid).all()[0].username
    # 获取对应的申报任务
    train = Train.query.join(TUT).join(UTrain).filter(UTrain.id == utrain.id).all()[0]
    # 获取文件
    data = utrain.datas
    filedata = {'image':[],'pdf': [], 'word': []}
    for datai in data:
        filedata[datai.type].append(datai.name)
    #培训名，培训内容，用户名，提交时间,pdf,word，图片
    da={"name":train.name,"main":train.main,"username":name,"uptime":str(utrain.uptime),"pdf":filedata["pdf"],"word":filedata["word"],"image":filedata["image"]}
    return Response(json.dumps(da), mimetype='application/json')

#通过用户申请培训
@main.route('/tgabilityuser', methods=['GET', 'POST'])
def tgabilityuser():
    if request.method == 'GET':
        id = request.args.get('id')
    else:
        id = request.form.get('id')
    # 修改申请状态
    utrain = UTrain.query.filter_by(id=id).first()
    utrain.type = 1
    db.session.add(utrain)
    db.session.commit()
    return Response(json.dumps({'status': True}), mimetype='application/json')