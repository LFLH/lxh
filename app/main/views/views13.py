#/useractivity的后端API
from flask import request,jsonify,session,redirect,Response
from app.main import main
from app.models.models import User,Activity,AD,Data,Declare,UDeclare,Train,UTrain,Score,System
from app import db
import json,datetime,random,string
from sqlalchemy import or_,and_

@main.after_app_request
def after_request(response):
    response.headers['Access-Control-Allow-Origin'] = '*'
    response.headers['Access-Control-Allow-Methods'] = 'PUT,GET,POST,DELETE'
    response.headers['Access-Control-Allow-Headers'] = 'Content-Type,Authorization'
    return response

#列表显示自主活动信息
@main.route('/showactivity',methods=['GET', 'POST'])
def showactivity():
    if request.method == "GET":
        page = request.args.get('page')#当前页
        per_page=request.args.get('per_page')#平均页数
    else:
        page = request.json.get('page')
        per_page = request.json.get('per_page')
    user = session.get('user')
    userid = user['userid']
    page=int(page)
    per_page=int(per_page)
    activity = Activity.query.filter(Activity.userid == userid).filter(Activity.status!=3).order_by(-Activity.updatetime).paginate(page, per_page, error_out=False)
    items = activity.items
    item = []
    count = (int(page) - 1) * int(per_page)
    for i in range(len(items)):
        itemss = {'number': count + i + 1, 'id': items[i].id, 'activityname': items[i].name,'type':items[i].type,
                  'begintime': str(items[i].begintime),"endtime":str(items[i].endtime),"main":items[i].main,"status":items[i].status}
        item.append(itemss)
    data = {'zpage': activity.pages, 'total': activity.total, 'dpage': activity.page, 'item': item}
    return Response(json.dumps(data), mimetype='application/json')

#添加新的申报任务
@main.route('/detailactivity',methods=['GET','POST'])
def detailactivity():
    return Response(json.dumps({}), mimetype='application/json')

#添加新的申报任务
@main.route('/updateactivity',methods=['GET','POST'])
def updateactivity():
    return Response(json.dumps({}), mimetype='application/json')

#删除自主活动
@main.route('/deleteactivity',methods=['GET', 'POST'])
def deleteactivity():
    if request.method == "GET":
        id = request.args.get('id')
        page = request.args.get('page')  # 当前页
        per_page = request.args.get('per_page')  # 平均页数
    else:
        id = request.json.get('id')
        page = request.json.get('page')  # 当前页
        per_page = request.json.get('per_page')  # 平均页数
    page = int(page)
    per_page = int(per_page)
    activity = Activity.query.filter(Activity.id == id).all()[0]
    activity.status=3
    db.session.add(activity)
    db.session.commit()
    userid=session.get('user')['userid']
    activity2 = Activity.query.filter(Activity.userid == userid).filter(Activity.status!=3).order_by(-Activity.updatetime).paginate(page, per_page,error_out=False)
    items = activity2.items
    item = []
    count = (int(page) - 1) * int(per_page)
    for i in range(len(items)):
        itemss = {'number': count + i + 1, 'id': items[i].id, 'activityname': items[i].name,
                  'type': items[i].type,'begintime': str(items[i].begintime), "endtime": str(items[i].endtime), 'status': items[i].status}
        item.append(itemss)
    data = {'zpage': activity2.pages, 'total': activity2.total, 'dpage': activity2.page, 'item': item}
    #data = sadetail(page, per_page)
    return Response(json.dumps(data), mimetype='application/json')