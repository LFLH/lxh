#/manageactivity的后端API
from flask import request,jsonify,session,redirect,Response
from app.main import main
from app.models.models import User,Activity,AD,Data
from app import db
import json,datetime

@main.after_app_request
def after_request(response):
    response.headers['Access-Control-Allow-Origin'] = '*'
    response.headers['Access-Control-Allow-Methods'] = 'PUT,GET,POST,DELETE'
    response.headers['Access-Control-Allow-Headers'] = 'Content-Type,Authorization'
    return response

#添加系统活动
@main.route('/addsysactivity', methods=['GET', 'POST'])
def addsysactivity():
    if request.method == 'GET':
        name = request.args.get('name')
        typeuser = '自主'
        type = request.args.get('type')
        begintime = request.args.get('begintime')
        endtime = request.args.get('endtime')
        stoptime = request.args.get('stoptime')
        main = request.args.get('main')
    else:
        name = request.form.get('name')
        typeuser = '自主'
        type = request.form.get('type')
        begintime = request.form.get('begintime')
        endtime = request.form.get('endtime')
        stoptime = request.form.get('stoptime')
        main = request.form.get('main')
    username = session.get('username')
    begintime = datetime.datetime.strptime(begintime, '%Y-%m-%d')
    endtime = datetime.datetime.strptime(endtime, '%Y-%m-%d')
    stoptime = stoptime.datetime.strptime(stoptime, '%Y-%m-%d')
    user = User.query.filter(User.username == username).all()[0]
    userid = 1
    activity = Activity(name=name, begintime=begintime, endtime=endtime, stoptime=stoptime, main=main, type=type, userid=userid)
    db.session.add(activity)
    db.session.commit()
    user.updatetime = activity.uptime
    db.session.add(user)
    db.session.commit()
    session["activityid"] = activity.id
    return Response(json.dumps({'status': True}), mimetype='application/json')

#列表显示活动
@main.route('/searchactivity',methods=['GET', 'POST'])
def searchactivity():
    if request.method == "GET":
        page = request.args.get('page')#当前页
        per_page=request.args.get('per_page')#平均页数
    else:
        page = request.json.get('page')
        per_page = request.json.get('per_page')
    page = int(page)
    per_page = int(per_page)
    activity = Activity.query.filter(Activity.status != 3).order_by(-Activity.updatetime).paginate(page, per_page, error_out=False)
    items = activity.items
    item = []
    count = (int(page) - 1) * int(per_page)
    for i in range(len(items)):
        itemss = {'number': count + i + 1, 'id': items[i].id, 'activityname': items[i].name, 'typeuser':items[i].typeuser,'type': items[i].type,
                  'begintime': str(items[i].begintime), "endtime": str(items[i].endtime),'status':items[i].status}
        item.append(itemss)
    data = {'zpage': activity.pages, 'total': activity.total, 'dpage': activity.page, 'item': item}
    return Response(json.dumps(data), mimetype='application/json')

#查看自主活动信息
@main.route('/detailuseractivity',methods=['GET', 'POST'])
def detailuseractivity():
    if request.method == "GET":
        id = request.args.get('id')
    else:
        id = request.json.get('id')
    activity=Activity.query.filter(Activity.id==id).all()[0]
    data=activity.datas
    filedata={'video':[],'music':[],'image':[],'pdf':[],'word':[]}
    for datai in data:
        filedata[datai.type].append(datai.name)
    da={'name':activity.name,'typeuser':activity.typeuser,'type':activity.type,'begintime':str(activity.begintime),'endtime':str(activity.endtime),'main':activity.main,'video':filedata['video'],'music':filedata['music'],'image':filedata['image'],'pdf':filedata['pdf'],'word':filedata['word']}
    return Response(json.dumps(da), mimetype='application/json')

#通过自主活动
@main.route('/tguseractivity', methods=['GET', 'POST'])
def tguseractivity():
    if request.method == 'GET':
        name = request.args.get('name')
    else:
        name = request.form.get('name')
    activity = Activity.query.filter_by(name=name).first()
    activity.status = 2
    db.session.commit()
    return Response(json.dumps({'status': True}), mimetype='application/json')

#驳回自主活动
@main.route('/bhuseractivity', methods=['GET', 'POST'])
def bhuseractivity():
    if request.method == 'GET':
        name = request.args.get('name')
    else:
        name = request.form.get('name')
    activity = Activity.query.filter_by(name=name).first()
    activity.status = 1
    db.session.commit()
    return Response(json.dumps({'status': True}), mimetype='application/json')

#查看系统活动信息
@main.route('/detailsysactivity',methods=['GET','POST'])
def detailsysactivity():
    if request.method == "GET":
        id = request.args.get('id')
    else:
        id = request.json.get('id')
    activity=Activity.query.filter(Activity.id==id).all()[0]
    userz=activity.users
    user=[]
    for users in userz:
        user.append(users.username)
    da={'name':activity.name,'typeuser':activity.typeuser,'type':activity.type,'begintime':str(activity.begintime),'endtime':str(activity.endtime),'main':activity.main,'user':user}
    return Response(json.dumps(da), mimetype='application/json')

#生成报名表
@main.route('/xlsxsysactivity',methods=['GET','POST'])
def xlsxsysactivity():
    return Response(json.dumps({}), mimetype='application/json')

#生成二维码
@main.route('/ewmsysactivity',methods=['GET','POST'])
def ewmsysactivity():
    return Response(json.dumps({}), mimetype='application/json')