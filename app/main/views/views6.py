#/manageabilityuser的后端API
from flask import request,jsonify,session,redirect,Response
from app.main import main
from app.models.models import User,Activity,AD,Data,Declare,UDeclare,Train,UTrain,TUT
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
def tsutrain(username,name,uptime,status,page,per_page):
    if username!=None:
        s1=(User.username==username)
    else:
        s1=True
    if name!=None:
        s2=(Train.name==name)
    else:
        s2=True
    if uptime!=None:
        s3=(UTrain.uptime==uptime)
    else:
        s3=True
    if status is None:
        s4=True
    else:
        status=int(status)
        if status==4:#未启用的培训，即被作废的培训
            s4=and_(Train.status==1)
        elif status<10:#用户未删除且系统发布培训未过期0,1,2
            s4=and_(User.checked==1,Train.status==0,Train.endtime>datetime.datetime.now(),UTrain.type==status)#0未通过，1通过，2驳回
        elif status<20:#用户未删除且系统发布培训过期10,11,12
            s4=and_(User.checked==1,Train.status==0,Train.endtime<datetime.datetime.now(),UTrain.type==status-10)#10未通过，11通过，12驳回
        elif status<30:#用户被删除且系统发布申报任务未过期20,21,22
            s4=and_(User.checked!=1,Train.status==0,Train.endtime>datetime.datetime.now(),UTrain.type==status-20)#20未通过，21通过，22驳回
        elif status<40:#用户被删除且系统发布申报任务过期30,31,32
            s4=and_(User.checked!=1,Train.status==0,Train.endtime<datetime.datetime.now(),UTrain.type==status-30)#30未通过，31通过，32驳回
    utrain=UTrain.query.join(TUT).join(Train).join(User).filter(and_(s1,s2,s3,s4)).order_by(-UTrain.uptime).paginate(page, per_page, error_out=False)
    return utrain


# 列表显示用户申请培训信息
@main.route('/searchabilityuser',methods=['GET','POST'])
def searchabilityuser():
    if request.method == "GET":
        page = request.args.get('page')#当前页
        per_page=request.args.get('per_page')#平均页数
        #检索条件
        username=request.args.get('username')#用户名
        name=request.args.get('name')#培训任务名
        uptime=request.args.get('uptime')#用户提交时间
        status=request.args.get('status')#状态
    else:
        page = request.form.get('page')
        per_page = request.form.get('per_page')
        # 检索条件
        username = request.form.get('username')  # 用户名
        name = request.form.get('name')  # 培训任务名
        uptime = request.form.get('uptime')  # 用户提交时间
        status = request.form.get('status')  # 状态
    page = int(page)
    per_page = int(per_page)
    # 连表查询未过期的用户申请培训
    #utrain=UTrain.query.join(TUT).join(Train).filter(Train.endtime>datetime.datetime.now()).order_by(-UTrain.uptime).paginate(page, per_page, error_out=False)
    utrain=tsutrain(username,name,uptime,status,page,per_page)
    items = utrain.items
    item = []
    count = (int(page) - 1) * int(per_page)
    for i in range(len(items)):
        # 获取用户名
        username = User.query.filter_by(id=items[i].userid).all()[0].username
        # 获取对应的培训任务
        train = Train.query.join(TUT).join(UTrain).filter(UTrain.id == items[i].id).all()[0]
        # 用户申请状态
        user = User.query.filter(User.id == items[i].userid).all()[0]
        if user.checked==1:
            if train.status==0:
                if train.endtime > datetime.datetime.now():
                    if items[i].type == 1:
                        status = 1  # 用户申请通过
                    elif items[i].type == 0:
                        status = 0  # 用户申请未通过
                    elif items[i].type == 2:
                        status=2#用户申请被驳回
                elif items[i].type == 1:
                    status = 11  # 用户申请通过但系统发布申请培训过期
                elif items[i].type == 0:
                    status = 10  # 用户申请未通过但系统发布申请培训过期
                elif items[i].type == 2:
                    status=12#用户申请被驳回但系统发布申请培训过期
            else:
                status=4#未启用的培训，即被作废的培训
        else:
            if train.status==0:
                if train.endtime > datetime.datetime.now():
                    if items[i].type == 1:
                        status = 21  # 用户被删除但用户申请通过
                    elif items[i].type == 0:
                        status = 20  # 用户被删除但用户申请未通过
                    elif items[i].type == 2:
                        status = 22  # 用户被删除但用户申请被驳回
                elif items[i].type == 1:
                    status = 31  # 用户被删除但用户申请通过但系统发布申请培训过期
                elif items[i].type == 0:
                    status = 30  # 用户被删除但用户申请未通过但系统发布申请培训过期
                elif items[i].type == 2:
                    status = 32  # 用户被删除但用户申请被驳回但系统发布申请培训过期
            else:
                status=4#未启用的培训，即被作废的培训
        # 返回id，用户名，培训名，培训起始时间，结束时间，提交时间，能否点击通过按钮的状态
        # (1通过，0未通过，11用户申请通过但系统发布申请培训过期，10用户申请未通过但系统发布申请培训过期，2未启用的培训，即被作废的培训)
        #（21用户被删除但用户申请通过，20用户被删除但用户申请未通过，31用户被删除但用户申请通过但系统发布申请培训过期，30用户被删除但用户申请未通过但系统发布申请培训过期）
        itemss = {'number': count + i + 1, 'id': items[i].id, 'username': username,'name':train.name,'begintime': str(train.begintime),
                  'endtime': str(train.endtime), 'uptime': str(items[i].uptime),'status':status}
        item.append(itemss)
    # 返回总页数、活动总数、当前页、用户申请集合
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
    # 获取对应的申请任务
    train = Train.query.join(TUT).join(UTrain).filter(UTrain.id == utrain.id).all()[0]
    # 获取文件
    data = utrain.datas
    filedata = {'image':[],'pdf': [], 'word': []}
    for datai in data:
        dataz = {'name': datai.name, 'path': datai.path, 'newname': datai.newname}
        filedata[datai.type].append(dataz)
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

#驳回用户申请培训
@main.route('/bhabilityuser', methods=['GET', 'POST'])
def bhabilityuser():
    if request.method == 'GET':
        id = request.args.get('id')
    else:
        id = request.form.get('id')
    # 修改申请状态
    utrain = UTrain.query.filter_by(id=id).first()
    utrain.type = 2
    db.session.add(utrain)
    db.session.commit()
    return Response(json.dumps({'status': True}), mimetype='application/json')