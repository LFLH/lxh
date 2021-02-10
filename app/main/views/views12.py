#/olduser的后端API
from flask import request,jsonify,session,redirect,Response
from app.main import main
from app.models.models import User,Activity,AD,Data,Declare,UDeclare,Train,UTrain,Score,System,TUT,AU
from app import db
import json,datetime,random,string
from sqlalchemy import or_,and_

@main.after_app_request
def after_request(response):
    response.headers['Access-Control-Allow-Origin'] = '*'
    response.headers['Access-Control-Allow-Methods'] = 'PUT,GET,POST,DELETE'
    response.headers['Access-Control-Allow-Headers'] = 'Content-Type,Authorization'
    return response

#计算百分比保留一位小数
def zbfb(a,b):
    if b!=0:
        m=a/b*1000
        mi=int(m)
        km=m-mi
        if km>0.5:
            mi=mi+1
        k=mi/10
        return k,100-k
    else:
        return 0.0,100.0

# 获取用户提交活动数、系统要求参与数、各月提交数、被驳回的活动信息，培训申请状态，新活动发布，新培训发布，活动报名截止，培训报名截止
@main.route('/olduserall',methods=['GET','POST'])
def olduserall():
    #需要提交数目
    count=int(System.query.filter(System.type=='count').all()[0].main)
    #已提交活动数目
    user=session.get('user')
    userid=user['userid']
    year = str(datetime.datetime.now()).split('-')[0]
    jyear = year + '-01-01 00:00:00'
    acount=Activity.query.filter(and_(Activity.userid==userid,Activity.updatetime>jyear,Activity.status!=3)).count()
    # 转保留一位小数的百分比
    #ya, wa = zbfb(acount, count)
    ya=acount
    wa=count-acount
    a={"ya":ya,"wa":wa}
    # 各月活动提交情况
    year = str(datetime.datetime.now()).split('-')[0]
    month = []
    for i in range(12):
        time = year + '-' + str(i + 1) + '-01 00:00:00'
        month.append(datetime.datetime.strptime(time, '%Y-%m-%d %H:%M:%S'))
    new = str(int(year) + 1) + '-01-01 00:00:00'
    month.append(datetime.datetime.strptime(new, '%Y-%m-%d %H:%M:%S'))
    activitycount = []
    for i in range(12):
        # 按月查询
        activity = Activity.query.filter(and_(Activity.updatetime >= month[i], Activity.updatetime < month[i + 1],Activity.userid==userid,Activity.status!=3)).count()
        activitycount.append(activity)
    message=[]
    #被驳回的活动信息
    activitybh=Activity.query.filter(and_(Activity.updatetime >= month[i],Activity.userid==userid,Activity.status==2)).all()
    for bh in activitybh:
        s=bh.name+"被驳回了"
        message.append(s)
    #培训申请状态
    utrain=UTrain.query.filter(and_(UTrain.userid==userid,UTrain.type==0)).all()
    for ut in utrain:
        train=Train.query.join(TUT).join(UTrain).filter(and_(UTrain.id==ut.id,Train.status==0)).all()
        if len(train)>0:
            if train[0].endtime>datetime.datetime.now():
                s=train[0].name+"申请未通过"
                message.append(s)
    #新活动发布
    activitynew=Activity.query.filter(and_(Activity.typeuser=="系统",Activity.stoptime>datetime.datetime.now(),Activity.status!=3)).all()
    for new in activitynew:
        ua=User.query.join(AU).join(Activity).filter(and_(Activity.id==new.id,User.id==userid)).count()
        if ua==0:
            s=new.name+"系统任务发布"
            message.append(s)
    #新培训发布
    trainnew=Train.query.filter(and_(Train.endtime>datetime.datetime.now(),Train.status!=1)).all()
    for tn in trainnew:
        utt=UTrain.query.join(TUT).join(Train).filter(and_(Train.id==tn.id,UTrain.userid==userid)).count()
        if utt==0:
            s=tn.name+"新培训发布了"
            message.append(s)
    #活动报名截止
    activityold=Activity.query.filter(and_(Activity.typeuser=="系统",Activity.stoptime<datetime.datetime.now(),Activity.status!=3)).all()
    for old in activityold:
        s=old.name+"系统任务报名截止了"
        message.append(s)
    #培训报名截止
    trainold = Train.query.filter(and_(Train.endtime < datetime.datetime.now(),Train.status!=1)).all()
    for to in trainold:
        s = to.name + "系统任务报名截止了"
        message.append(s)
    #返回已提交活动占比，各月提交情况，各种信息（被驳回的活动信息，培训申请状态，新活动发布，新培训发布，活动报名截止，培训报名截止）
    return Response(json.dumps({"a":a,"activitycount":activitycount,"message":message}), mimetype='application/json')