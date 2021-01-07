from flask import request, jsonify, Response
from app.main import main
from app.models.models import User, Activity, AD, Data
from app import db
import os, json
import random, string


@main.after_app_request
def after_request(response):
    response.headers['Access-Control-Allow-Origin'] = '*'
    response.headers['Access-Control-Allow-Methods'] = 'PUT,GET,POST,DELETE'
    response.headers['Access-Control-Allow-Headers'] = 'Content-Type,Authorization'
    return response


@main.route('/adduser', methods=['GET', 'POST'])
def adduser():
    if request.method == "GET":
        username = request.args.get('username')
        name = request.args.get('name')
    else:
        username = request.json.get('username')
        name = request.json.get('name')
    k = random.randint(8, 20)
    password = ''.join(random.sample(string.ascii_letters + string.digits, k))
    user = User(username=username, name=name, password=password, type='user', checked=0)
    db.session.add(user)
    db.session.commit()
    return Response(json.dumps({'status': True}), mimetype='application/json')


@main.route('/searchuser', methods=['GET', 'POST'])
def searchuser():
    if request.method == "GET":
        page = request.args.get('page')  # 当前页
        per_page = request.args.get('per_page')  # 平均页数
    else:
        page = request.json.get('page')
        per_page = request.json.get('per_page')
    # 倒叙：在排序的时候使用这个字段的字符串名字，然后在前面加一个负号
    page = int(page)
    per_page = int(per_page)
    # 查询用户需要sysadmin用户和老用户、未过期用户
    user = User.query.filter(User.status != 'delete').order_by(-User.updatetime).paginate(page, per_page,
                                                                                          error_out=False)
    items = user.items
    item = []
    count = (int(page) - 1) * int(per_page)
    for i in range(len(items)):
        itemss = {'number': count + i + 1, 'id': items[i].id, 'username': items[i].username,
                  'lasttime': str(items[i].updatetime)}
        item.append(itemss)
    data = {'zpage': user.pages, 'total': user.total, 'dpage': user.page, 'item': item}
    return Response(json.dumps(data), mimetype='application/json')


@main.route('/deleteuser', methods=['GET', 'POST'])
def deleteuser():
    if request.method == "GET":
        id = request.args.get('id')
        page = request.args.get('page')  # 当前页
        per_page = request.args.get('per_page')  # 平均页数
    else:
        id = request.json.get('id')
        page = request.json.get('page')
        per_page = request.json.get('per_page')
    # 移除用户的相关活动及数据
    page = int(page)
    per_page = int(per_page)
    user = User.query.filter(User.id == id).all()[0]
    user.checked = 0
    activitys = Activity.query.filter(Activity.userid == id).all()
    for activity in activitys:
        activity.status = "delete"
        db.session.add(activity)
    db.session.commit()
    db.session.add(user)
    db.session.commit()
    # 倒叙：在排序的时候使用这个字段的字符串名字，然后在前面加一个负号
    user = User.query.filter(User.status != 'delete').order_by(-User.updatetime).paginate(page, per_page,
                                                                                          error_out=False)
    items = user.items
    item = []
    count = (int(page) - 1) * int(per_page)
    for i in range(len(items)):
        itemss = {'number': count + i + 1, 'id': items[i].id, 'username': items[i].username,
                  'lasttime': str(items[i].updatetime)}
        item.append(itemss)
    data = {'zpage': user.pages, 'total': user.total, 'dpage': user.page, 'item': item}
    return Response(json.dumps(data), mimetype='application/json')
