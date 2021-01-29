#/login的后端API
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
        session['user']={'name':user[0].name,'username':user[0].username,'userid':user[0].id,'usertype':user[0].type,'checked':user[0].checked}
        #return jsonify([{'type': user[0].type, 'status': True}])
        if(user[0].type=='sysadmin'):#管理员登录
            return Response(json.dumps({'type': user[0].type, 'status': True,'checked':user[0].checked}), mimetype='application/json')
        elif(user[0].checked==1):#老用户
            return Response(json.dumps({'type': user[0].type, 'status': True,'checked':user[0].checked}), mimetype='application/json')
        elif(user[0].endtime>datetime.datetime.now()):#新用户
            return Response(json.dumps({'type': user[0].type, 'status': True, 'checked': user[0].checked}),mimetype='application/json')
        else:#过期用户
            return Response(json.dumps({'status': False}), mimetype='application/json')
    else:#错误登录
        #return jsonify([{'status': False}])
        return Response(json.dumps({'status': False}), mimetype='application/json')
