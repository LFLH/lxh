#/managedeclareadd的后端API
from flask import request,jsonify,session,redirect,Response
from app.main import main
from app.models.models import User,Activity,AD,Data,Declare,UDeclare,DUDC
from app import db
import json,datetime
from sqlalchemy import or_,and_

@main.after_app_request
def after_request(response):
    response.headers['Access-Control-Allow-Origin'] = '*'
    response.headers['Access-Control-Allow-Methods'] = 'PUT,GET,POST,DELETE'
    response.headers['Access-Control-Allow-Headers'] = 'Content-Type,Authorization'
    return response

#列表显示申报任务
@main.route('/searchdeclare',methods=['GET','POST'])
def searchdeclare():
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
    declare=Declare.query.order_by(-Declare.createtime).paginate(page, per_page, error_out=False)
    items = declare.items
    item = []
    count = (int(page) - 1) * int(per_page)
    for i in range(len(items)):
        if declare.status == 0:
            if items[i].endtime>datetime.datetime.now():
                status=1#申报未过期
            else:
                status=0#申报过期
        else:
            status=2#未启用的申报，即被作废的申报
        # 返回用户id，用户名，密码，最后操作时间，状态
        itemss = {'number': count + i + 1, 'id': items[i].id, 'name': items[i].name,
                  'createtime': str(items[i].createtime), 'begintime': str(items[i].begintime) ,'endtime': str(items[i].endtime) ,'status': status}
        item.append(itemss)
    # 返回总页数、活动总数、当前页、用户集合
    data = {'zpage': declare.pages, 'total': declare.total, 'dpage': declare.page, 'item': item}
    return Response(json.dumps(data), mimetype='application/json')

#查看详细申报任务
@main.route('/detaildeclare',methods=['GET','POST'])
def detaildeclare():
    # 根据活动id查找申报
    if request.method == "GET":
        id = request.args.get('id')
    else:
        #id = request.json.get('id')
        id = request.form.get('id')
    declare = Declare.query.filter(Declare.id==id).all()[0]
    udeclare=UDeclare.query.join(DUDC).join(Declare).filter(Declare.id==declare.id).all()
    user=[]
    for ud in udeclare:
        userud=User.query.filter(User.id==ud.userid).all()[0]
        #用户名，申报时间，申报状态
        user.append({'username':userud.name,'uptime':str(ud.uptime),'status':ud.type})
    # 返回申报任务名、创建时间、开始时间、结束时间、活动内容、用户组
    da = {'name': declare.name, 'createtime':str(declare.createtime),
          'begintime': str(declare.begintime), 'endtime': str(declare.endtime), 'main': declare.main, 'user': user}
    return Response(json.dumps(da), mimetype='application/json')

#修改申报任务
@main.route('/updatedeclare',methods=['GET','POST'])
def updatedeclare():
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
    declare = Declare.query.filter(Declare.id == id).all()[0]
    chatime =datetime.datetime.now()-declare.endtime
    chatime=chatime.days
    if chatime>1:
        return Response(json.dumps({'status': False}), mimetype='application/json')
    #修改申报信息
    else:
        edtime=declare.endtime
        declare.name=name
        declare.begintime=begintime
        declare.endtime=endtime
        declare.main=main
        db.session.add(declare)
        db.session.commit()
        # 设置新用户提交时间
        user = User.query.filter(and_(User.checked == 0, User.type == 'user', User.endtime == edtime)).all()
        for i in range(len(user)):
            user[i].endtime = endtime
            db.session.add(user[i])
            db.session.commit()
        return Response(json.dumps({'status': True}), mimetype='application/json')


#删除申报任务
@main.route('/deletedeclare',methods=['GET','POST'])
def deletedeclare():
    if request.method == "GET":
        id=request.args.get('id')
    else:
        id = request.form.get('id')
    declare = Declare.query.filter(Declare.id == id).all()[0]
    chatime = datetime.datetime.now() - declare.endtime
    chatime = chatime.days
    if chatime > 1:#过期申报
        return Response(json.dumps({'status': False}), mimetype='application/json')
    else:
        udeclare = UDeclare.query.join(DUDC).join(Declare).filter(Declare.id == declare.id).count()
        if udeclare>0:#已有人申报
            declare.status = 1
            db.session.add(declare)
            db.session.commit()
            return Response(json.dumps({'status': True}), mimetype='application/json')
        else:#全新申报
            declare.status=1
            db.session.add(declare)
            db.session.commit()
            return Response(json.dumps({'status': True}), mimetype='application/json')

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
    maxdate = '9999-12-31 23:59:59'
    maxdate = datetime.datetime.strptime(maxdate, '%Y-%m-%d %H:%M:%S')
    user=User.query.filter(and_(User.checked==0,User.type=='user',User.endtime==maxdate)).all()
    for i in range(len(user)):
        user[i].endtime=endtime
        db.session.add(user[i])
        db.session.commit()
    return Response(json.dumps({'status':True}), mimetype='application/json')