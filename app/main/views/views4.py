#/managedeclareuser的后端API
from flask import request,jsonify,session,redirect,Response
from app.main import main
from app.models.models import User,Activity,AD,Data,Declare,UDeclare,DUDC
from app import db
import json,datetime

@main.after_app_request
def after_request(response):
    response.headers['Access-Control-Allow-Origin'] = '*'
    response.headers['Access-Control-Allow-Methods'] = 'PUT,GET,POST,DELETE'
    response.headers['Access-Control-Allow-Headers'] = 'Content-Type,Authorization'
    return response

#列表显示用户申报信息
@main.route('/searchdeclareuser',methods=['GET','POST'])
def searchdeclareuser():
    if request.method == "GET":
        page = request.args.get('page')#当前页
        per_page=request.args.get('per_page')#平均页数
    else:
        page = request.form.get('page')
        per_page = request.form.get('per_page')
        #page = request.json.get('page')
        #per_page = request.json.get('per_page')
    page = int(page)
    per_page = int(per_page)
    #连表查询未过期的用户申报
    udeclare=UDeclare.query.join(DUDC).join(Declare).order_by(-UDeclare.uptime).paginate(page, per_page, error_out=False)
    items = udeclare.items
    item = []
    count = (int(page) - 1) * int(per_page)
    for i in range(len(items)):
        #获取用户名
        name = User.query.filter_by(id=items[i].userid).all()[0].username
        #获取对应的申报任务
        declare=Declare.query.join(DUDC).join(UDeclare).filter(UDeclare.id==items[i].id).all()[0]
        #用户申报状态
        # user = User.query.filter(User, id == items[i].userid).all()[0]
        user = User.query.filter(User.id == items[i].userid).all()[0]
        if user.checked==2:
            if declare.status==0:
                if declare.endtime>datetime.datetime.now():
                    if items[i].type == 1:
                        status = 21#用户被删除但用户申报通过
                    else:
                        status = 20  # 用户被删除但用户申报未通过
                elif items[i].type==1:
                    status=31#用户被删除但用户申报通过但系统发布申报任务过期
                else:
                    status=30#用户被删除但用户申报未通过但系统发布申报任务过期
            else:
                status=2#未启用的申报，即被作废的申报
        else:
            if declare.status==0:
                if declare.endtime>datetime.datetime.now():
                    if items[i].type == 1:
                        status = 1#用户申报通过
                    else:
                        status = 0  # 用户申报未通过
                elif items[i].type==1:
                    status=11#用户申报通过但系统发布申报任务过期
                else:
                    status=10#用户申报未通过但系统发布申报任务过期
            else:
                status=2#未启用的申报，即被作废的申报
        #返回id，用户名，申报起始时间，结束时间，提交时间,能否点击通过按钮的状态
        # (1通过，0未通过，11用户申报通过但系统发布申报任务过期，10用户申报未通过但系统发布申报任务过期，2未启用的培训，即被作废的培训)
        # （21用户被删除但用户申报通过，20用户被删除但用户申报未通过，31用户被删除但用户申请通过但系统发布申报任务过期，30用户被删除但用户申请未通过但系统发布申报任务过期）
        itemss = {'number': count + i + 1, 'id': items[i].id, 'name': name, 'begintime': str(declare.begintime),'endtime': str(declare.endtime),'uptime': str(items[i].uptime),'status':status}
        item.append(itemss)
    # 返回总页数、活动总数、当前页、用户申报集合
    data = {'zpage': udeclare.pages, 'total': udeclare.total, 'dpage': udeclare.page, 'item': item}
    return Response(json.dumps(data), mimetype='application/json')

#显示用户申报的详细信息
@main.route('/detaildeclareuser',methods=['GET','POST'])
def detaildeclareuser():
    if request.method == 'GET':
        id = request.args.get('id')
    else:
        id = request.form.get('id')
    #获取用户申报
    udeclare=UDeclare.query.filter(UDeclare.id==id).all()[0]
    # 获取用户名
    name = User.query.filter_by(id=udeclare.userid).all()[0].username
    # 获取对应的申报任务
    declare = Declare.query.join(DUDC).join(UDeclare).filter(UDeclare.id == udeclare.id).all()[0]
    #获取文件
    data=udeclare.datas
    filedata = {'pdf': [], 'word': []}
    for datai in data:
        dataz = {'name': datai.name, 'path': datai.path, 'newname': datai.newname}
        filedata[datai.type].append(dataz)
    #用户名，申报起始时间，结束时间，提交时间,pdf,word
    da={'name':name,'begintime': str(declare.begintime),'endtime': str(declare.endtime),'uptime': str(udeclare.uptime),'pdf':filedata['pdf'],'word':filedata['word']}
    return Response(json.dumps(da), mimetype='application/json')

#通过用户申报
@main.route('/tgdeclareuser', methods=['GET', 'POST'])
def tgdeclareuser():
    if request.method == 'GET':
        id = request.args.get('id')
    else:
        id = request.form.get('id')
    #修改申请状态
    udeclare = UDeclare.query.filter_by(id=id).first()
    udeclare.type = 1
    db.session.add(udeclare)
    db.session.commit()
    #修改用户状态
    user=User.query.filter(User.id==udeclare.userid).all()[0]
    user.checked=1
    db.session.add(user)
    db.session.commit()
    return Response(json.dumps({'status': True}), mimetype='application/json')