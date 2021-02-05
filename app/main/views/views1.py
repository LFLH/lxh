#/login的后端API
from flask import request,jsonify,session,redirect,Response
from app.main import main
from app.models.models import User,Activity,AD,Data,Declare,DU
from app import db
import json,datetime

@main.after_app_request
def after_request(response):
    response.headers['Access-Control-Allow-Origin'] = '*'
    response.headers['Access-Control-Allow-Methods'] = 'PUT,GET,POST,DELETE'
    response.headers['Access-Control-Allow-Headers'] = 'Content-Type,Authorization'
    return response

#用户登录
@main.route('/userlogin', methods=['GET', 'POST'])
def userlogin():
    if request.method == "GET":
        username = request.args.get('username')
        password=request.args.get('password')
    else:
        #username = request.json.get('username')
        #password = request.json.get('password')
        username = request.form.get('username')
        password = request.form.get('password')
    user=User.query.filter(User.username==username,User.password==password).all()
    if len(user)>0:
        if(user[0].type=='sysadmin'):#管理员登录
            session['user'] = {'name': user[0].name, 'username': user[0].username, 'userid': user[0].id,'usertype': user[0].type, 'checked': user[0].checked,'declare':True}
            data={'type': user[0].type, 'status': True,'checked':user[0].checked}
        elif(user[0].checked==1):#老用户
            session['user'] = {'name': user[0].name, 'username': user[0].username, 'userid': user[0].id,'usertype': user[0].type, 'checked': user[0].checked, 'declare': True}
            data = {'type': user[0].type, 'status': True, 'checked': user[0].checked}
        elif(user[0].endtime>datetime.datetime.now()):#新用户
            declare=Declare.query.join(DU).join(User).filter(User.id==user[0].id).all()
            if(len(declare)>0):#添加申报任务的用户
                session['user'] = {'name': user[0].name, 'username': user[0].username, 'userid': user[0].id,'usertype': user[0].type, 'checked': user[0].checked, 'declare': True}
                data = {'type': user[0].type, 'status': True, 'checked': user[0].checked}
            else:#未被添加申报任务的用户
                data={'status': False}
        else:#过期用户
            data = {'status': False}
    else:#错误登录
        data = {'status': False}
    print(data)
    return Response(json.dumps(data), mimetype='application/json')

