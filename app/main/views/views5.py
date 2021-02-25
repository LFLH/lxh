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

#条件检索
def tsdeclare(name,createtime,begintime,endtime,status,page,per_page):
    if name!=None:
        #s1=(Declare.name==name)
        s1=(Declare.name.contains(name))
    else:
        s1=True
    if createtime!=None:
        s2=(Declare.createtime==createtime)
    else:
        s2=True
    if begintime!=None:
        s3=(Declare.begintime==begintime)
    else:
        s3=True
    if endtime!=None:
        s4=(Declare.endtime==endtime)
    else:
        s4=True
    if status is None:
        s5=True
    else:
        status=int(status)
        if status==0:#申报未过期
            s5=and_(Declare.status==0,Declare.endtime>datetime.datetime.now())
        elif status==1:#申报过期
            s5=and_(Declare.status==0,Declare.endtime<datetime.datetime.now())
        elif status==2:#未启用的申报，即被作废的申报
            s5=(Declare.status==1)
    declare=Declare.query.filter(and_(s1,s2,s3,s4,s5)).order_by(-Declare.createtime).paginate(page, per_page, error_out=False)
    return declare

#列表显示申报任务
@main.route('/searchdeclare',methods=['GET','POST'])
def searchdeclare():
    if request.method == "GET":
        page = request.args.get('page')#当前页
        per_page=request.args.get('per_page')#平均页数
        #检索条件
        name = request.args.get('name')  # 申报名
        createtime = request.args.get('createtime')  # 申报创建时间
        begintime = request.args.get('begintime')  # 申报开始时间
        endtime = request.args.get('endtime')  # 申报结束时间
        status = request.args.get('status')  # 申报状态
    else:
        page = request.form.get('page')
        per_page = request.form.get('per_page')
        # 检索条件
        name = request.form.get('name')  # 申报名
        createtime = request.form.get('createtime')  # 申报创建时间
        begintime = request.form.get('begintime')  # 申报开始时间
        endtime = request.form.get('endtime')  # 申报结束时间
        status = request.form.get('status')  # 申报状态
    #倒叙：在排序的时候使用这个字段的字符串名字，然后在前面加一个负号
    page=int(page)
    per_page = int(per_page)
    #declare=Declare.query.order_by(-Declare.createtime).paginate(page, per_page, error_out=False)
    declare=tsdeclare(name,createtime,begintime,endtime,status,page,per_page)
    items = declare.items
    item = []
    count = (int(page) - 1) * int(per_page)
    for i in range(len(items)):
        if items[i].status == 0:
            if items[i].endtime>datetime.datetime.now():
                status=0#申报未过期
            else:
                status=1#申报过期
        else:
            status=2#未启用的申报，即被作废的申报
        # 返回用户id，用户名，密码，最后操作时间，状态
        itemss = {'number': count + i + 1, 'id': items[i].id, 'name': items[i].name,
                  'createtime': str(items[i].createtime), 'begintime': str(items[i].begintime) ,'endtime': str(items[i].endtime) ,'status': status}
        item.append(itemss)
    # 返回总页数、活动总数、当前页、用户集合
    data = {'zpage': declare.pages, 'total': declare.total, 'dpage': declare.page, 'item': item}
    return Response(json.dumps(data), mimetype='application/json')

#需申报的用户
@main.route('/getnewuser',methods=['GET','POST'])
def getnewuser():
    user=User.query.filter(and_(User.type=='user',User.checked!=1)).all()
    userz = []
    for u in user:
        userz.append({'name':u.name,'username':u.username,'userid':u.id})
    return Response(json.dumps({'userz': userz}), mimetype='application/json')

#新增申报的用户
@main.route('/addnewuser',methods=['GET','POST'])
def addnewuser():
    if request.method == "GET":
        id = request.args.get('id')
    else:
        #id = request.json.get('id')
        id=request.form.get('id')
    userz = request.values.getlist('userz[]')
    declare=Declare.query.filter(Declare.id==id).all()[0]
    for u in userz:
        user=User.query.filter(User.id==u).all()[0]
        declare.users.append(user)
        user.checked=0
        user.endtime=declare.endtime
        db.session.add(user)
        db.session.commit()
    db.session.add(declare)
    db.session.commit()
    return Response(json.dumps({'status': True}), mimetype='application/json')

#删除申报的用户
@main.route('/deletenewuser',methods=['GET','POST'])
def deletenewuser():
    if request.method == "GET":
        id = request.args.get('id')
    else:
        #id = request.json.get('id')
        id=request.form.get('id')
    userz = request.values.getlist('userz[]')
    declare=Declare.query.filter(Declare.id==id).all()[0]
    users=declare.users
    # 移除申报中的用户
    length = len(users)
    for i in range(length):
        users[length - i - 1].status=2
        db.session.add(users[length - i - 1])
        db.session.commit()
        declare.users.remove(users[length - i - 1])
    for usersi in userz:
        user=User.query.filter(User.id==usersi).all()[0]
        user.status=0
        db.session.add(user)
        db.session.commit()
        declare.users.append(user)
    db.session.add(declare)
    db.session.commit()
    return Response(json.dumps({'status': True}), mimetype='application/json')

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

#详细申报任务页的条件检索
def tjsearchdetaildeclare(id,username,name,status):
    if username!=None:
        s1=(User.username.contains(username))
    else:
        s1=True
    if name!=None:
        s2=(User.name.contains(name))
    else:
        s2=True
    if status is None:
        s3=True
    else:
        status=int(status)
        s3=(UDeclare.type==status)
    udeclare=UDeclare.query.join(User).join(DUDC).join(Declare).filter(and_(s1,s2,s3,Declare.id==id)).all()
    return udeclare

#详细申报任务页的列表展示
@main.route('/detaildeclaresearch',methods=['GET','POST'])
def detaildeclaresearch():
    if request.method == "GET":
        id=request.args.get('id')#申报id
        #检索条件
        username=request.args.get('username')#账户
        name=request.args.get('name')#用户名
        status=request.args.get('status')#状态
    else:
        id = request.form.get('id')  # 申报id
        # 检索条件
        username = request.form.get('username')  # 账户
        name = request.form.get('name')  # 用户名
        status = request.form.get('status')  # 状态
    udeclare=tjsearchdetaildeclare(id,username,name,status)
    user = []
    for ud in udeclare:
        userud = User.query.filter(User.id == ud.userid).all()[0]
        # 用户名，申报时间，申报状态
        user.append({'username': userud.name, 'uptime': str(ud.uptime), 'status': ud.type})
    da = {'user': user}
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
    if begintime!=None:
        begintime = datetime.datetime.strptime(begintime, '%Y-%m-%d')
    if endtime!=None:
        endtime = datetime.datetime.strptime(endtime, '%Y-%m-%d')
    declare = Declare.query.filter(Declare.id == id).all()[0]
     # chatime =datetime.datetime.now()-declare.endtime
    # chatime=chatime.days
    # if chatime>1:
    if datetime.datetime.now() > declare.endtime:
        return Response(json.dumps({'status': False}), mimetype='application/json')
    if declare.status != 0:
        return Response(json.dumps({'status': False}), mimetype='application/json')
    #修改申报信息
    else:
        if name!=None:
            declare.name=name
        if begintime!=None:
            declare.begintime=begintime
        if endtime!=None:
            declare.endtime=endtime
        if main!=None:
            declare.main=main
        db.session.add(declare)
        db.session.commit()
        # 设置新用户提交时间
        user = declare.user
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
     # chatime = datetime.datetime.now() - declare.endtime
    # chatime = chatime.days
    # if chatime > 1:#过期申报
    if datetime.datetime.now() > declare.endtime:
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
    #添加申报用户
    userz = request.values.getlist('userz[]')
    for u in userz:
        user=User.query.filter(User.id==u).all()[0]
        declare.users.append(user)
        user.checked=0
        user.endtime=declare.endtime
        db.session.add(user)
        db.session.commit()
    db.session.add(declare)
    db.session.commit()
    id=declare.id
    return Response(json.dumps({'status':True,'id':id}), mimetype='application/json')