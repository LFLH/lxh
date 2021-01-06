"""
    自主活动
"""
from flask import request, jsonify, Response
from app.main import main
from app.models.models import UDeclare, Activity, Declare, DUDC, User, Train
from app import db
import os, json, datetime, time


# 通过自主活动
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


# 驳回自主活动
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


# 删除自主活动
@main.route('/deleteactivity', methods=['GET', 'POST'])
def deleteactivity():
    if request.method == 'GET':
        name = request.args.get('name')
    else:
        name = request.form.get('name')
    activity = Activity.query.filter_by(name=name).first()
    db.session.delete(activity)
    db.session.commit()
    return Response(json.dumps({'status': True}), mimetype='application/json')