#前端界面展示
from flask import render_template,session,redirect,request
from app.models.models import Activity,User,AU
from app.main import main
import datetime

@main.after_app_request
def after_request(response):
    response.headers['Access-Control-Allow-Origin'] = '*'
    response.headers['Access-Control-Allow-Methods'] = 'PUT,GET,POST,DELETE'
    response.headers['Access-Control-Allow-Headers'] = 'Content-Type,Authorization'
    return response

#扫码签到
@main.route('/useractivitysign/<string:activityid>',methods=['GET','POST'])
def useractivitysign(activityid):
    activityid=int(activityid)
    activity=Activity.query.filter(Activity.id==activityid).all()[0]
    if activity.endtime<datetime.datetime.now():
        s='/useractivitysign/'+str(activityid)+'/fail'
        return redirect(s)
    else:
        return render_template('useractivitysign.html')

#扫码过期
@main.route('/useractivitysign/<string:activityid>/fail',methods=['GET','POST'])
def useractivitysignfail(activityid):
    return render_template('useractivitysignfail.html')

#签到成功
@main.route('/useractivitysign/<string:activityid>/success',methods=['GET','POST'])
def useractivitysignsuccess(activityid):
    return render_template('useractivitysignsuccess.html')

@main.route('/')
def index():
    return redirect('/login')

#用户登录
@main.route('/login',methods=['GET','POST'])
def login():
    user = session.get('user')
    if user!=None:
        session.pop('username', None)
    return render_template('login.html')

#管理员登录后页
@main.route('/manage',methods=['GET','POST'])
def manage():
    user = session.get('user')
    if user == None:
        return redirect('/login')
    elif user['usertype']!='sysadmin' :
        if user['checked']==1:
            return redirect('/olduser')
        else:
            return redirect('/newuser')
    else:
        return render_template('manage.html',name=user["name"],username=user["username"])

#活动管理
@main.route('/manageactivity',methods=['GET','POST'])
def manageactivity():
    user = session.get('user')
    if user == None:
        return redirect('/login')
    elif user['usertype'] != 'sysadmin':
        if user['checked'] == 1:
            return redirect('/olduser')
        else:
            return redirect('/newuser')
    else:
        return render_template('manageactivity.html',name=user["name"],username=user["username"])

#申报用户管理
@main.route('/managedeclareuser',methods=['GET','POST'])
def managedeclareuser():
    user = session.get('user')
    if user == None:
        return redirect('/login')
    elif user['usertype'] != 'sysadmin':
        if user['checked'] == 1:
            return redirect('/olduser')
        else:
            return redirect('/newuser')
    else:
        return render_template('managedeclareuser.html',name=user["name"],username=user["username"])

#申报任务添加
@main.route('/managedeclareadd',methods=['GET','POST'])
def managedeclareadd():
    user = session.get('user')
    if user == None:
        return redirect('/login')
    elif user['usertype'] != 'sysadmin':
        if user['checked'] == 1:
            return redirect('/olduser')
        else:
            return redirect('/newuser')
    else:
        return render_template('managedeclareadd.html',name=user["name"],username=user["username"])
#跳转到能力提升培训任务添加的单独界面
@main.route('/managedeclareadd_new',methods=['GET','POST'])
def managedeclareadd_new():
    user = session.get('user')
    return render_template('managedeclareadd_new.html', name=user["name"],username=user["username"])

#能力提升培训用户管理
@main.route('/manageabilityuser',methods=['GET','POST'])
def manageabilityuser():
    user = session.get('user')
    if user == None:
        return redirect('/login')
    elif user['usertype'] != 'sysadmin':
        if user['checked'] == 1:
            return redirect('/olduser')
        else:
            return redirect('/newuser')
    else:
        return render_template('manageabilityuser.html',name=user["name"],username=user["username"])

#能力提升培训任务添加
@main.route('/manageabilityadd',methods=['GET','POST'])
def manageabilityadd():
    user = session.get('user')
    if user == None:
        return redirect('/login')
    elif user['usertype'] != 'sysadmin':
        if user['checked'] == 1:
            return redirect('/olduser')
        else:
            return redirect('/newuser')
    else:
        return render_template('manageabilityadd.html',name=user["name"],username=user["username"])
#跳转到能力提升培训任务添加的单独界面
@main.route('/manageabilityadd_new',methods=['GET','POST'])
def manageabilityadd_new():
    user = session.get('user')
    return render_template('manageabilityadd_new.html', name=user["name"],username=user["username"])

#考核管理
@main.route('/manageexamine',methods=['GET','POST'])
def manageexamine():
    user = session.get('user')
    if user == None:
        return redirect('/login')
    elif user['usertype'] != 'sysadmin':
        if user['checked'] == 1:
            return redirect('/olduser')
        else:
            return redirect('/newuser')
    else:
        return render_template('manageexamine.html',name=user["name"],username=user["username"])

#用户管理
@main.route('/manageuser',methods=['GET','POST'])
def manageuser():
    user = session.get('user')
    if user == None:
        return redirect('/login')
    elif user['usertype'] != 'sysadmin':
        if user['checked'] == 1:
            return redirect('/olduser')
        else:
            return redirect('/newuser')
    else:
        return render_template('manageuser.html',name=user["name"],username=user["username"])

#系统设置
@main.route('/managesystem',methods=['GET','POST'])
def managesystem():
    user = session.get('user')
    if user == None:
        return redirect('/login')
    elif user['usertype'] != 'sysadmin':
        if user['checked'] == 1:
            return redirect('/olduser')
        else:
            return redirect('/newuser')
    else:
        return render_template('managesystem.html',name=user["name"],username=user["username"])

#新用户界面
@main.route('/newuser',methods=['GET','POST'])
def newuser():
    user = session.get('user')
    print(user)
    if user == None:
        return redirect('/login')
    elif user['usertype']=='sysadmin':
        return redirect('/manage')
    elif user['checked']==1:
        return redirect('/olduser')
    else:
        return render_template('newuser.html',name=user["name"],username=user["username"])
#新用户申报
@main.route('/newuser_declare', methods=['GET','POST'])
def newuser_declare():
    user = session.get('user')
    return render_template('newuser_declare.html',name=user["name"],username=user["username"])
#老用户界面
@main.route('/olduser',methods=['GET','POST'])
def olduser():
    user = session.get('user')
    if user == None:
        return redirect('/login')
    elif user['usertype'] == 'sysadmin':
        return redirect('/manage')
    elif user['checked'] == 0:
        return redirect('/newuser')
    else:
        return render_template('olduser.html',name=user["name"],username=user["username"])
#老用户账户设置界面
@main.route('/user_setting',methods=['GET','POST'])
def user_setting():
    user = session.get('user')
    return render_template('user_setting.html',name=user["name"],username=user["username"])
#用户已提交活动
@main.route('/useractivity',methods=['GET','POST'])
def useractivity():
    user = session.get('user')
    if user == None:
        return redirect('/login')
    elif user['usertype'] == 'sysadmin':
        return redirect('/manage')
    elif user['checked'] == 0:
        return redirect('/newuser')
    else:
        return render_template('useractivity.html',name=user["name"],username=user["username"])

#自主活动提交
@main.route('/userupdata',methods=['GET','POST'])
def userupdata():
    user = session.get('user')
    if user==None:
        return redirect('/login')
    elif user['usertype'] == 'sysadmin':
        return redirect('/manage')
    elif user['checked'] == 0:
        return redirect('/newuser')
    else:
        return render_template('userupdata.html',name=user["name"],username=user["username"])

#系统活动查看
@main.route('/useractivityregister',methods=['GET','POST'])
def useractivityregister():
    user = session.get('user')
    if user==None:
        return redirect('/login')
    elif user['usertype'] == 'sysadmin':
        return redirect('/manage')
    elif user['checked'] == 0:
        return redirect('/newuser')
    else:
        return render_template('useractivityregister.html',name=user["name"],username=user["username"])

#系统培训查看
@main.route('/usertrainregister',methods=['GET','POST'])
def usertrainregister():
    user = session.get('user')
    if user==None:
        return redirect('/login')
    elif user['usertype'] == 'sysadmin':
        return redirect('/manage')
    elif user['checked'] == 0:
        return redirect('/newuser')
    else:
        return render_template('usertrainregister.html',name=user["name"],username=user["username"])

#年度报告提交
@main.route('/userndreport',methods=['GET','POST'])
def userndreport():
    user = session.get('user')
    if user==None:
        return redirect('/login')
    elif user['usertype'] == 'sysadmin':
        return redirect('/manage')
    elif user['checked'] == 0:
        return redirect('/newuser')
    else:
        return render_template('userndreport.html',name=user["name"],username=user["username"])

#科技周报告提交
@main.route('/userkjzreport',methods=['GET','POST'])
def userkjzreport():
    user = session.get('user')
    if user==None:
        return redirect('/login')
    elif user['usertype'] == 'sysadmin':
        return redirect('/manage')
    elif user['checked'] == 0:
        return redirect('/newuser')
    else:
        return render_template('userkjzreport.html',name=user["name"],username=user["username"])