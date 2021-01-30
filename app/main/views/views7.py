#/manageabilityadd的后端API
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

#列表显示申报任务
@main.route('/searchtrain',methods=['GET','POST'])
def searchtrain():
    if request.method == "GET":
        page = request.args.get('page')#当前页
        per_page=request.args.get('per_page')#平均页数
    else:
        page = request.form.get('page')
        per_page = request.form.get('per_page')
        #page = request.json.get('page')
        #per_page = request.json.get('per_page')
    #倒叙：在排序的时候使用这个字段的字符串名字，然后在前面加一个负号
    page=int(page)
    per_page = int(per_page)
    train=Train.query.order_by(-Train.createtime).paginate(page, per_page, error_out=False)
    items = train.items
    item = []
    count = (int(page) - 1) * int(per_page)
    for i in range(len(items)):
        if train.status == 0:
            if items[i].endtime>datetime.datetime.now():
                status=1#培训未过期
            else:
                status=0#培训过期
        else:
            status=2#未启用的培训，即被作废的培训
        # 返回用户id，用户名，密码，最后操作时间，状态
        itemss = {'number': count + i + 1, 'id': items[i].id, 'name': items[i].name,
                  'createtime': str(items[i].createtime), 'begintime': str(items[i].begintime) ,'endtime': str(items[i].endtime) ,'status': status}
        item.append(itemss)
    # 返回总页数、活动总数、当前页、用户集合
    data = {'zpage': train.pages, 'total': train.total, 'dpage': train.page, 'item': item}
    return Response(json.dumps(data), mimetype='application/json')

#查看详细申报任务
@main.route('/detailtrain',methods=['GET','POST'])
def detailtrain():
    # 根据活动id查找申报
    if request.method == "GET":
        id = request.args.get('id')
    else:
        #id = request.json.get('id')
        id = request.form.get('id')
    train = Train.query.filter(Train.id==id).all()[0]
    utrain=UTrain.query.join(TUT).join(Train).filter(Train.id==train.id).all()
    user=[]
    for ud in utrain:
        userud=User.query.filter(User.id==ud.userid).all()[0]
        #用户名，申报时间，申报状态
        user.append({'username':userud.name,'uptime':str(ud.uptime),'status':ud.type})
    # 返回申报任务名、创建时间、开始时间、结束时间、活动内容、用户组
    da = {'name': train.name, 'createtime':str(train.createtime),
          'begintime': str(train.begintime), 'endtime': str(train.endtime), 'main': train.main, 'user': user}
    return Response(json.dumps(da), mimetype='application/json')

#修改培训任务
@main.route('/updatetrain',methods=['GET','POST'])
def updatetrain():
    if request.method == "GET":
        id=request.args.get('id')
        name = request.args.get('name')
        begintime = request.args.get('begintime')
        endtime = request.args.get('endtime')
        main = request.args.get('main')
    else:
        id = request.form.get('id')
        name = request.form.get('name')
        begintime = request.form.get('begintime')
        endtime = request.form.get('endtime')
        main = request.form.get('main')
    begintime = datetime.datetime.strptime(begintime, '%Y-%m-%d')
    endtime = datetime.datetime.strptime(endtime, '%Y-%m-%d')
    train = Train.query.filter(Train.id == id).all()[0]
    chatime =datetime.datetime.now()-train.endtime
    chatime=chatime.days
    if chatime>1:
        return Response(json.dumps({'status': False}), mimetype='application/json')
    #修改培训信息
    else:
        train.name=name
        train.begintime=begintime
        train.endtime=endtime
        train.main=main
        db.session.add(train)
        db.session.commit()
        return Response(json.dumps({'status': True}), mimetype='application/json')

#删除申报任务
@main.route('/deletetrain',methods=['GET','POST'])
def deletetrain():
    if request.method == "GET":
        id=request.args.get('id')
    else:
        id = request.form.get('id')
    train = Train.query.filter(Train.id == id).all()[0]
    chatime = datetime.datetime.now() - train.endtime
    chatime = chatime.days
    if chatime > 1:#过期申请
        return Response(json.dumps({'status': False}), mimetype='application/json')
    else:
        utrain = UTrain.query.join(TUT).join(Train).filter(Train.id == train.id).count()
        if utrain>0:#已有人申请
            train.status = 1
            db.session.add(train)
            db.session.commit()
            return Response(json.dumps({'status': True}), mimetype='application/json')
        else:#全新申请
            train.status=1
            db.session.add(train)
            db.session.commit()
            return Response(json.dumps({'status': True}), mimetype='application/json')

#添加新的培训
@main.route('/addability',methods=['GET','POST'])
def addability():
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
    #创建能力提升培训
    train=Train(name=name,begintime=begintime,endtime=endtime,main=main)
    db.session.add(train)
    db.session.commit()
    return Response(json.dumps({'status':True}), mimetype='application/json')