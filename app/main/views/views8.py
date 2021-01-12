#/manageexamine的后端API
from flask import request,jsonify,session,redirect,Response
from app.main import main
from app.models.models import User,Activity,AD,Data,Declare,UDeclare,Train,UTrain,Score
from app import db
import json,datetime

@main.after_app_request
def after_request(response):
    response.headers['Access-Control-Allow-Origin'] = '*'
    response.headers['Access-Control-Allow-Methods'] = 'PUT,GET,POST,DELETE'
    response.headers['Access-Control-Allow-Headers'] = 'Content-Type,Authorization'
    return response

# 显示分数
@main.route('/showscore')
def showscore():
    scores = Score.query.all()
    result = {}
    for score in scores:
        name = User.query.filter_by(id=score.userid).first().username
        if name not in result:
            result.update({name: [{score.year: score.score}]})
        else:
            result[name].append({score.year: score.score})
    return jsonify(result)