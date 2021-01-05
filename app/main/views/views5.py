from flask import render_template,session,redirect,request
from app.main import main
from urllib import request as request2
import json

@main.after_app_request
def after_request(response):
    response.headers['Access-Control-Allow-Origin'] = '*'
    response.headers['Access-Control-Allow-Methods'] = 'PUT,GET,POST,DELETE'
    response.headers['Access-Control-Allow-Headers'] = 'Content-Type,Authorization'
    return response

@main.route('/')
def index():
    return redirect('/login')

@main.route('/login',methods=['GET','POST'])
def login():
    user = session.get('user')
    if user!=None:
        session.pop('username', None)
    return render_template('login.html')

@main.route('/userupdata',methods=['GET','POST'])
def userupdata():
    user = session.get('user')
    if user==None:
        return redirect('/login')
    else:
        return render_template('userupdata.html',username=user["username"])

@main.route('/useractivity',methods=['GET','POST'])
def useractivity():
    user = session.get('user')
    if user == None:
        return redirect('/login')
    else:
        return render_template('useractivity.html',username=user["username"])

@main.route('/manageuser',methods=['GET','POST'])
def manageuser():
    user = session.get('user')
    if user == None:
        return redirect('/login')
    else:
        return render_template('manageuser.html',username=user["username"])

@main.route('/manageactivity',methods=['GET','POST'])
def manageactivity():
    user = session.get('user')
    if user == None:
        return redirect('/login')
    else:
        return render_template('manageactivity.html',username=user["username"])

@main.route('/manageaddtype',methods=['GET','POST'])
def manageaddtype():
    user = session.get('user')
    if user == None:
        return redirect('/login')
    else:
        return render_template('manageaddtype.html', username=user["username"])