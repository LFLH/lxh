#/manageexamine的后端API
from flask import request,jsonify,session,redirect,Response
from app.main import main
from app.models.models import User,Activity,AD,Data,Declare,UDeclare,Train,UTrain,Score
from app import db
import json,datetime
from sqlalchemy import or_,and_

@main.after_app_request
def after_request(response):
    response.headers['Access-Control-Allow-Origin'] = '*'
    response.headers['Access-Control-Allow-Methods'] = 'PUT,GET,POST,DELETE'
    response.headers['Access-Control-Allow-Headers'] = 'Content-Type,Authorization'
    return response

#条件检索
def tsscore(username,activitycount,onys,twys,thys,page,per_page):
    year = int(datetime.datetime.now().strftime('%Y'))
    if username!=None:
        s1=(User.username==username)
    else:
        s1=True
    if onys!=None:
        onys=int(onys)
        s2=and_(Score.year==year-2,Score.score==onys)
    else:
        s2=True
    if twys!=None:
        twys=int(twys)
        s3=and_(Score.year==year-1,Score.score==twys)
    else:
        s3=True
    if thys!=None:
        thys=int(thys)
        s4=and_(Score.year==year,Score.score==thys)
    else:
        s4=True
    if activitycount is None:
        s5=True
    else:
        activitycount=int(activitycount)
        Year = str(year) + '-01-01 00:00:00'
        Year = datetime.datetime.strptime(Year, '%Y-%m-%d %H:%M:%S')
        items=User.query.filter(and_(User.checked == 1,User.type != 'sysadmin')).order_by(-User.updatetime).all()
        u=[]
        for i in range(len(items)):
            ac=Activity.query.filter(and_(Activity.userid == items[i].id, Activity.updatetime > Year)).count()
            if ac==activitycount:
                u.append(items[i].id)
        s5=(User.id.in_(u))
    user=User.query.join(Score).filter(and_(s1,s2,s3,s4,s5,User.checked == 1,User.type != 'sysadmin')).order_by(-User.updatetime).paginate(page, per_page, error_out=False)
    return user

# 显示分数
@main.route('/showscore',methods=['GET','POST'])
def showscore():
    if request.method == "GET":
        page = request.args.get('page')#当前页
        per_page=request.args.get('per_page')#平均页数
        #检索条件
        username=request.args.get('username')#用户名
        activitycount=request.args.get('activitycount')#参与活动次数
        onys=request.args.get('onys')#考核第一年分数
        twys=request.args.get('twys')#考核第二年分数
        thys=request.args.get('thys')#考核第三年分数
    else:
        page = request.form.get('page')
        per_page = request.form.get('per_page')
        # 检索条件
        username = request.form.get('username')  # 用户名
        activitycount = request.form.get('activitycount')  # 参与活动次数
        onys = request.form.get('onys')  # 考核第一年分数
        twys = request.form.get('twys')  # 考核第二年分数
        thys = request.form.get('thys')  # 考核第三年分数
    page = int(page)
    per_page = int(per_page)
    #获取当前年数
    year=int(datetime.datetime.now().strftime('%Y'))
    #查询老用户
    #user = User.query.filter(and_(User.checked == 1,User.type != 'sysadmin')).order_by(-User.updatetime).paginate(page, per_page, error_out=False)
    user=tsscore(username,activitycount,onys,twys,thys,page,per_page)
    items = user.items
    item = []
    count = (int(page) - 1) * int(per_page)
    #设置年份起始点
    Year=str(year)+'-01-01 00:00:00'
    Year=datetime.datetime.strptime(Year, '%Y-%m-%d %H:%M:%S')
    for i in range(len(items)):
        #查询当年活动次数
        activitycount=Activity.query.filter(and_(Activity.userid==items[i].id,Activity.updatetime>Year)).count()
        #查询分数
        score1=Score.query.filter(and_(Score.userid==items[i].id,Score.year==year-2)).all()
        if len(score1)>0:
            onys=score1[0].score
        else:
            onys=''
        score2 = Score.query.filter(and_(Score.userid == items[i].id, Score.year == year - 1)).all()
        if len(score2)>0:
            twys=score2[0].score
        else:
            twys=''
        score3 = Score.query.filter(and_(Score.userid == items[i].id, Score.year == year )).all()
        if len(score3)>0:
            thys=score3[0].score
        else:
            thys=''
        #返回用户id,用户名，活动次数，前年分数，去年分数，今年分数
        itemss={'number':count+i+1,'id':items[i].id,'username':items[i].username,'activitycount':activitycount,'onys':onys,'twys':twys,'thys':thys}
        item.append(itemss)
    # 返回总页数、活动总数、当前页、用户分数集合
    data={'zpage':user.pages,'total':user.total,'dpage':user.page,'item':item}
    return Response(json.dumps(data), mimetype='application/json')

#分数设置
@main.route('/dfscore',methods=['GET','POST'])
def dfscore():
    if request.method == "GET":
        id = request.args.get('id')#当前页
        score=request.args.get('score')#平均页数
    else:
        id = request.form.get('id')
        score = request.form.get('score')
    # 获取当前年数
    year = int(datetime.datetime.now().strftime('%Y'))
    score=int(score)
    scores=Score.query.filter(and_(Score.userid==id,Score.year==year)).all()
    if len(scores)>0:
        scores[0].score=score
        db.session.add(scores[0])
        db.session.commit()
    else:
        newscore=Score(userid=id,year=year,score=score)
        db.session.add(newscore)
        db.session.commit()
    return Response(json.dumps({'status': True}), mimetype='application/json')