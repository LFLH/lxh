#/useractivityregister的后端API
from flask import request,jsonify,session,redirect,Response
from app.main import main
from app.models.models import User,Activity,AD,Data,Declare,UDeclare,Train,UTrain,Score,System,AU
from app import db
import json,datetime,random,string,os
from sqlalchemy import or_,and_
from werkzeug.utils import secure_filename

@main.after_app_request
def after_request(response):
    response.headers['Access-Control-Allow-Origin'] = '*'
    response.headers['Access-Control-Allow-Methods'] = 'PUT,GET,POST,DELETE'
    response.headers['Access-Control-Allow-Headers'] = 'Content-Type,Authorization'
    return response

# 列表查看系统活动
@main.route('/searchsysactivity', methods=['GET', 'POST'])
def searchsysactivity():
    if request.method == "GET":
        page = request.args.get('page')#当前页
        per_page=request.args.get('per_page')#平均页数
    else:
        page = request.json.get('page')
        per_page = request.json.get('per_page')
    page=int(page)
    per_page=int(per_page)
    user=session.get('user')
    userid=user['userid']
    activity = Activity.query.filter(and_(Activity.typeuser=="系统",Activity.status!=3)).order_by(-Activity.updatetime).paginate(page, per_page, error_out=False)
    items = activity.items
    item = []
    count = (int(page) - 1) * int(per_page)
    for i in range(len(items)):
        if items[i].stoptime<datetime.datetime.now():
            status=1#已过期
        else:
            au=AU.query.filter(and_(AU.userid==userid,AU.activityid==items[i].id)).count()
            if au>0:
                status=2#已报名
            else:
                status=0#未报名
        # 返回活动名、活动类型、开始时间、结束时间、活动内容、状态
        itemss = {'number': count + i + 1, 'id': items[i].id, 'activityname': items[i].name, 'type': items[i].type,
                  'begintime': str(items[i].begintime), "endtime": str(items[i].endtime), "main": items[i].main,
                  "status": status}
        item.append(itemss)
    # 返回总页数、活动总数、当前页、活动集合
    data = {'zpage': activity.pages, 'total': activity.total, 'dpage': activity.page, 'item': item}
    return Response(json.dumps(data), mimetype='application/json')

# 查看系统活动详细信息
@main.route('/detailsysactivitytouser', methods=['GET', 'POST'])
def detailsysactivitytouser():
    if request.method == 'GET':
        id = request.args.get('id')
    else:
        id = request.form.get('id')
    activity = Activity.query.filter_by(id=id).first()
    #返回活动名，活动类型，开始时间，结束时间，报名截止时间，活动内容
    result = {'name': activity.name, 'type': activity.type, 'begintime': str(activity.begintime),
              'endtime': str(activity.endtime),"stoptime":str(activity.stoptime), 'main': activity.main}
    return Response(json.dumps(result), mimetype='application/json')

# 系统活动报名
@main.route('/bmsysactivity', methods=['GET', 'POST'])
def bmsysactivity():
    if request.method == 'GET':
        id = request.args.get('id')
    else:
        id = request.form.get('id')
    activityid = id
    user=session.get('user')
    userid = user["userid"]
    #创建报名表
    au=AU(activityid=activityid,userid=userid)
    db.session.add(au)
    db.session.commit()
    return Response(json.dumps({'status': True}), mimetype='application/json')