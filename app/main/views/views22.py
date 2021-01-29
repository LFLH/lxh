#用户设置的后端API
from flask import request,jsonify,session,redirect,Response,make_response
from app.main import main
from app.models.models import User,Activity,AD,Data,Declare,UDeclare,Train,UTrain,Score,System,AU,Record
from app import db
import json,datetime,random,string,os,mimetypes
from sqlalchemy import or_,and_
from werkzeug.utils import secure_filename

@main.after_app_request
def after_request(response):
    response.headers['Access-Control-Allow-Origin'] = '*'
    response.headers['Access-Control-Allow-Methods'] = 'PUT,GET,POST,DELETE'
    response.headers['Access-Control-Allow-Headers'] = 'Content-Type,Authorization'
    return response

#获取用户信息
@main.route('/getuser',methods=['GET','POST'])
def getuser():
    user=session.get('user')
    userid=user['userid']
    user=User.query.filter(User.id==userid).all()[0]
    # 用户名,科普基地单位名称,邮箱,联系电话,地址,密码
    users={'username':user.username,'name':user.name,'email':user.email,'phone':user.phone,'address':user.address,'password':user.password}
    return Response(json.dumps(users), mimetype='application/json')

#修改用户信息
@main.route('/setuser',methods=['GET','POST'])
def setuser():
    if request.method == "GET":
        email = request.args.get('email')
        phone = request.args.get('phone')
        address = request.args.get('address')
        password = request.args.get('password')
    else:
        email = request.form.get('email')
        phone = request.form.get('phone')
        address = request.form.get('address')
        password = request.form.get('password')
    user = session.get('user')
    userid = user['userid']
    user = User.query.filter(User.id == userid).all()[0]
    #修改用户信息
    user.email=email
    user.phone=phone
    user.address=address
    user.password=password
    db.session.add(user)
    db.session.commit()
    return Response(json.dumps({'status':True}), mimetype='application/json')