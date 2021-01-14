#/manageuser的后端API
from flask import request,jsonify,session,redirect,Response
from app.main import main
from app.models.models import User,Activity,AD,Data,Declare,UDeclare,Train,UTrain,Score
from app import db
import json,datetime,random,string
from sqlalchemy import or_,and_

@main.after_app_request
def after_request(response):
    response.headers['Access-Control-Allow-Origin'] = '*'
    response.headers['Access-Control-Allow-Methods'] = 'PUT,GET,POST,DELETE'
    response.headers['Access-Control-Allow-Headers'] = 'Content-Type,Authorization'
    return response

#添加用户
@main.route('/adduser',methods=['GET', 'POST'])
def adduser():
    #根据用户名添加用户
    if request.method == "GET":
        username = request.args.get('username')
    else:
        username = request.json.get('username')
    user=User.query.filter(User.username==username).all()
    #不存在用户
    if len(user)==0:
        k = random.randint(8, 20)
        #自动生成密码
        password=''.join(random.sample(string.ascii_letters + string.digits, k))
        #添加用户
        newuser=User(username=username,password=password,type='user',checked=0)
        db.session.add(newuser)
        db.session.commit()
    #存在用户
    else:
        user[0].endtime=datetime.datetime.now()
        db.session.add(user[0])
        db.session.commit()
    return Response(json.dumps({'status': True}), mimetype='application/json')

#删除用户
@main.route('/deleteuser',methods=['GET', 'POST'])
def deleteuser():
    if request.method == "GET":
        id = request.args.get('id')
        page = request.args.get('page')  # 当前页
        per_page = request.args.get('per_page')  # 平均页数
    else:
        id = request.json.get('id')
        page = request.json.get('page')
        per_page = request.json.get('per_page')
    #移除用户的相关活动及数据
    page = int(page)
    per_page = int(per_page)
    user=User.query.filter(User.id==id).all()[0]
    user.checked=0
    activitys=Activity.query.filter(Activity.userid==id).all()
    for activity in activitys:
        activity.status=3
        db.session.add(activity)
    db.session.commit()
    db.session.add(user)
    db.session.commit()
    # 倒叙：在排序的时候使用这个字段的字符串名字，然后在前面加一个负号
    user = User.query.filter(and_(or_(User.checked == 1, and_(User.checked == 0, User.endtime > datetime.datetime.now()))),User.type != 'sysadmin').order_by(-User.updatetime).paginate(page, per_page, error_out=False)
    items = user.items
    item = []
    count = (int(page) - 1) * int(per_page)
    for i in range(len(items)):
        # 返回用户id，用户名，密码，最后操作时间，状态
        itemss = {'number': count + i + 1, 'id': items[i].id, 'username': items[i].username,
                  'password': items[i].password, 'lasttime': str(items[i].updatetime), 'status': items[i].checked}
        item.append(itemss)
    # 返回总页数、活动总数、当前页、用户集合
    data = {'zpage': user.pages, 'total': user.total, 'dpage': user.page, 'item': item}
    return Response(json.dumps(data), mimetype='application/json')

#列表显示用户
@main.route('/searchuser',methods=['GET', 'POST'])
def searchuser():
    if request.method == "GET":
        page = request.args.get('page')#当前页
        per_page=request.args.get('per_page')#平均页数
    else:
        page = request.json.get('page')
        per_page = request.json.get('per_page')
    #倒叙：在排序的时候使用这个字段的字符串名字，然后在前面加一个负号
    page=int(page)
    per_page = int(per_page)
    #查询用户需要sysadmin用户和老用户、未过期用户
    user=User.query.filter(and_(or_(User.checked==1,and_(User.checked==0,User.endtime>datetime.datetime.now())),User.type!='sysadmin')).order_by(-User.updatetime).paginate(page, per_page, error_out=False)
    items=user.items
    item=[]
    count=(int(page)-1)*int(per_page)
    for i in range(len(items)):
        #返回用户id，用户名，密码，最后操作时间，状态
        itemss={'number':count+i+1,'id':items[i].id,'username':items[i].username,'password':items[i].password,'lasttime':str(items[i].updatetime),'status':items[i].checked}
        item.append(itemss)
    # 返回总页数、活动总数、当前页、用户集合
    data={'zpage':user.pages,'total':user.total,'dpage':user.page,'item':item}
    return Response(json.dumps(data), mimetype='application/json')

