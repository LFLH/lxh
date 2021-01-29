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

# 显示分数
@main.route('/showscore',methods=['GET','POST'])
def showscore():
    if request.method == "GET":
        page = request.args.get('page')#当前页
        per_page=request.args.get('per_page')#平均页数
    else:
        page = request.form.get('page')
        per_page = request.form.get('per_page')
        #page = request.json.get('page')
        #per_page = request.json.get('per_page')
    page = int(page)
    per_page = int(per_page)
    #获取当前年数
    year=int(datetime.datetime.now().strftime('%Y'))
    #查询老用户
    user = User.query.filter(and_(User.checked == 1,User.type != 'sysadmin')).order_by(-User.updatetime).paginate(page, per_page, error_out=False)
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