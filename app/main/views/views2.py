#/manage的后端API
from flask import request,jsonify,session,redirect,Response
from app.main import main
from app.models.models import User,Activity,AD,Data,Declare,UDeclare,DUDC,Train,TUT,UTrain
from app import db
import json,datetime
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

#获取申报和参与申报的用户数、各月提交数、活动报名人数
@main.route('/manageall',methods=['GET','POST'])
def manageall():
    #需要申报人数
    declare=Declare.query.filter(and_(Declare.status==0,Declare.endtime>datetime.datetime.now())).order_by(-Declare.id).all()
    if len(declare)>0:
        declare=declare[0]
        usercount=len(declare.users)
        #已申报人数
        udeclarecount=UDeclare.query.join(DUDC).join(Declare).join(User).filter(Declare.id==declare.id,UDeclare.type!=2).count()
        #转保留一位小数的百分比
        #yd,wd=zbfb(udeclarecount,usercount)
        if usercount==0:
            yd=0.0
            wd=0.0
        else:
            yd=udeclarecount
            wd=usercount-udeclarecount
    else:
        yd=0.0
        wd=0.0
    d={"yd":yd,"wd":wd}
    #各月活动提交情况
    year=str(datetime.datetime.now()).split('-')[0]
    month=[]
    for i in range(12):
        time=year+'-'+str(i+1)+'-01 00:00:00'
        month.append(datetime.datetime.strptime(time, '%Y-%m-%d %H:%M:%S'))
    new=str(int(year)+1)+'-01-01 00:00:00'
    month.append(datetime.datetime.strptime(new, '%Y-%m-%d %H:%M:%S'))
    activitycount=[]
    for i in range(12):
        #按月查询
        activity=Activity.query.filter(and_(Activity.updatetime>=month[i],Activity.updatetime<month[i+1],Activity.typeuser=='自主',Activity.status!=3,Activity.status!=1)).count()
        activitycount.append(activity)
    #需要报名人数
    train=Train.query.filter(and_(Train.status==0)).order_by(-Train.id).all()
    if len(train)>0:
        train=train[0]
        usercount2=User.query.filter(and_(User.checked==1,User.type=='user')).count()
        #已报名培训人数
        utraincount=UTrain.query.join(TUT).join(Train).join(User).filter(and_(Train.id==train.id,User.checked==1,UTrain.type!=2)).count()
        # 转保留一位小数的百分比
        #yt,wt = zbfb(utraincount, usercount2)
        if usercount2==0:
            yt = 0.0
            wt = 0.0
        else:
            yt=utraincount
            wt=usercount2-utraincount
    else:
        yt=0.0
        wt=0.0
    t={"yt":yt,"wt":wt}
    #返回申报百分比，各月提交情况，新培训报名
    return Response(json.dumps({"d":d,"activitycount":activitycount,"t":t}), mimetype='application/json')