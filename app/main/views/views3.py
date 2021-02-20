#/manageactivity的后端API
from flask import request,jsonify,session,redirect,Response,send_from_directory,abort,make_response,send_file,render_template
from app.main import main
from app.models.models import User,Activity,AD,Data,AU
from app import db
from sqlalchemy import or_,and_
import json,datetime,xlwt,os,mimetypes,time,qrcode
import socket

@main.after_app_request
def after_request(response):
    response.headers['Access-Control-Allow-Origin'] = '*'
    response.headers['Access-Control-Allow-Methods'] = 'PUT,GET,POST,DELETE'
    response.headers['Access-Control-Allow-Headers'] = 'Content-Type,Authorization'
    return response

#添加系统活动
@main.route('/addsysactivity', methods=['GET', 'POST'])
def addsysactivity():
    #获取系统活动的活动名、活动类型、开始时间、结束时间、报名截止时间、活动内容
    if request.method == 'GET':
        name = request.args.get('name')
        type = request.args.get('type')
        begintime = request.args.get('begintime')
        endtime = request.args.get('endtime')
        stoptime = request.args.get('stoptime')
        main = request.args.get('main')
    else:
        name = request.form.get('name')
        type = request.form.get('type')
        begintime = request.form.get('begintime')
        endtime = request.form.get('endtime')
        stoptime = request.form.get('stoptime')
        main = request.form.get('main')
    user = session.get('user')
    #处理时间类型数据
    begintime = datetime.datetime.strptime(begintime, '%Y-%m-%d')
    endtime = datetime.datetime.strptime(endtime, '%Y-%m-%d')
    stoptime = datetime.datetime.strptime(stoptime, '%Y-%m-%d')
    userid = user['userid']
    #创建活动及存表
    activity = Activity(name=name, typeuser='系统',type=type, begintime=begintime, endtime=endtime, stoptime=stoptime, main=main, userid=userid)
    db.session.add(activity)
    db.session.commit()
    user2=User.query.filter(User.id==userid).all()[0]
    user2.updatetime = activity.updatetime
    db.session.add(user2)
    db.session.commit()
    return Response(json.dumps({'status': True}), mimetype='application/json')

#条件检索系统活动
def tsactivity1(name,type,status,page,per_page):
    if name!=None:
        s1=(Activity.name==name)
    else:
        s1=True
    if type!=None:
        s2=(Activity.type==type)
    else:
        s2=True
    if status!=None:
        status=int(status)
        if status<10:
            s3=(Activity.status==status)
        else:
            k=status-10
            s3=and_(Activity.status==k,User.checked!=1)
    else:
        s3=True
    activity=Activity.query.join(User).filter(and_(s1,s2,s3,Activity.typeuser=='系统')).order_by(-Activity.updatetime).paginate(page, per_page, error_out=False)
    return activity

#列表显示系统活动
@main.route('/searchmansysactivity',methods=['GET', 'POST'])
def searchmansysactivity():
    if request.method == "GET":
        page = request.args.get('page')#当前页
        per_page=request.args.get('per_page')#平均页数
        #检索条件
        name=request.args.get('name')#活动名
        type=request.args.get('type')#活动类型
        status=request.args.get('status')#状态
    else:
        page = request.form.get('page')
        per_page = request.form.get('per_page')
        # 检索条件
        name = request.form.get('name')  # 活动名
        type = request.form.get('type')  # 活动类型
        status = request.form.get('status')  # 状态
    page = int(page)
    per_page = int(per_page)
    #获取未删除活动倒叙
    activity=tsactivity1(name,type,status,page,per_page)
    #activity = Activity.query.order_by(-Activity.updatetime).paginate(page, per_page, error_out=False)
    items = activity.items
    item = []
    count = (int(page) - 1) * int(per_page)
    for i in range(len(items)):
        if items[i].typeuser=='自主':
            user=User.query.filter(User.id==items[i].userid).all()[0]
            if user.checked==1:
                status=items[i].status
            else:
                status=10+items[i].status
        else:
            status=items[i].status
        #number，活动id号，活动名，活动类别，活动类型，开始时间，结束时间，状态（0创建，1驳回，2通过，3删除，10+0，1，2，3因用户考核被删除的记录）
        itemss = {'number': count + i + 1, 'id': items[i].id, 'activityname': items[i].name, 'typeuser':items[i].typeuser,'type': items[i].type,
                  'begintime': str(items[i].begintime), "endtime": str(items[i].endtime),'status':status}
        item.append(itemss)
    #返回总页数、活动总数、当前页、活动集合
    data = {'zpage': activity.pages, 'total': activity.total, 'dpage': activity.page, 'item': item}
    return Response(json.dumps(data), mimetype='application/json')

#条件检索自主活动
def tsactivity2(name,type,status,page,per_page):
    if name!=None:
        s1=(Activity.name==name)
    else:
        s1=True
    if type!=None:
        s2=(Activity.type==type)
    else:
        s2=True
    if status!=None:
        status=int(status)
        if status<10:
            s3=(Activity.status==status)
        else:
            k=status-10
            s3=and_(Activity.status==k,User.checked!=1)
    else:
        s3=True
    activity=Activity.query.join(User).filter(and_(s1,s2,s3,Activity.typeuser=='自主')).order_by(-Activity.updatetime).paginate(page, per_page, error_out=False)
    return activity

#列表显示自主活动
@main.route('/searchzhactivity',methods=['GET', 'POST'])
def searchzhactivity():
    if request.method == "GET":
        page = request.args.get('page')#当前页
        per_page=request.args.get('per_page')#平均页数
        #检索条件
        name=request.args.get('name')#活动名
        type=request.args.get('type')#活动类型
        status=request.args.get('type')#状态
    else:
        page = request.form.get('page')
        per_page = request.form.get('per_page')
        # 检索条件
        name = request.form.get('name')  # 活动名
        type = request.form.get('type')  # 活动类型
        status = request.form.get('type')  # 状态
    page = int(page)
    per_page = int(per_page)
    #获取未删除活动倒叙
    activity=tsactivity2(name,type,status,page,per_page)
    #activity = Activity.query.order_by(-Activity.updatetime).paginate(page, per_page, error_out=False)
    items = activity.items
    item = []
    count = (int(page) - 1) * int(per_page)
    for i in range(len(items)):
        if items[i].typeuser=='自主':
            user=User.query.filter(User.id==items[i].userid).all()[0]
            if user.checked==1:
                status=items[i].status
            else:
                status=10+items[i].status
        else:
            status=items[i].status
        #number，活动id号，活动名，活动类别，活动类型，开始时间，结束时间，状态（0创建，1驳回，2通过，3删除，10+0，1，2，3因用户考核被删除的记录）
        itemss = {'number': count + i + 1, 'id': items[i].id, 'activityname': items[i].name, 'typeuser':items[i].typeuser,'type': items[i].type,
                  'begintime': str(items[i].begintime), "endtime": str(items[i].endtime),'status':status}
        item.append(itemss)
    #返回总页数、活动总数、当前页、活动集合
    data = {'zpage': activity.pages, 'total': activity.total, 'dpage': activity.page, 'item': item}
    return Response(json.dumps(data), mimetype='application/json')

#查看自主活动信息
@main.route('/detailuseractivity',methods=['GET', 'POST'])
def detailuseractivity():
    #根据活动id查找自主活动
    if request.method == "GET":
        id = request.args.get('id')
    else:
        id = request.form.get('id')
        #id = request.json.get('id')
    activity=Activity.query.filter(Activity.id==id).all()[0]
    user=User.query.filter(User.id==activity.userid).all()[0]
    #获取自主活动的文件名
    data=activity.datas
    filedata={'video':[],'music':[],'image':[],'pdf':[],'word':[]}
    for datai in data:
        dataz={'name':datai.name,'path':datai.path,'newname':datai.newname}
        filedata[datai.type].append(dataz)
    #返回活动名、活动类别、活动类型、开始时间、结束时间、活动内容、视频、音频、图片、pdf、word
    da={'username':user.username,'name':activity.name,'typeuser':activity.typeuser,'type':activity.type,'begintime':str(activity.begintime),'endtime':str(activity.endtime),'main':activity.main,'video':filedata['video'],'music':filedata['music'],'image':filedata['image'],'pdf':filedata['pdf'],'word':filedata['word']}
    return Response(json.dumps(da), mimetype='application/json')

#通过自主活动
@main.route('/tguseractivity', methods=['GET', 'POST'])
def tguseractivity():
    if request.method == 'GET':
        id = request.args.get('id')
    else:
        id = request.form.get('id')
    id=int(id)
    activity = Activity.query.filter(Activity.id==id).first()
    activity.status = 2#状态，0创建，1驳回，2通过，3删除，10+0，1，2，3因用户考核被删除的记录
    db.session.add(activity)
    db.session.commit()
    return Response(json.dumps({'status': True}), mimetype='application/json')

#驳回自主活动
@main.route('/bhuseractivity', methods=['GET', 'POST'])
def bhuseractivity():
    if request.method == 'GET':
        id = request.args.get('id')
    else:
        id = request.form.get('id')
    id=int(id)
    activity = Activity.query.filter(Activity.id==id).first()
    activity.status = 1#状态，0创建，1驳回，2通过，3删除，10+0，1，2，3因用户考核被删除的记录
    db.session.add(activity)
    db.session.commit()
    return Response(json.dumps({'status': True}), mimetype='application/json')

#查看系统活动信息
@main.route('/detailsysactivity',methods=['GET','POST'])
def detailsysactivity():
    # 根据活动id查找系统活动
    if request.method == "GET":
        id = request.args.get('id')
    else:
        id = request.form.get('id')
        #id = request.json.get('id')
    activity=Activity.query.filter(Activity.id==id).all()[0]
    # 获取系统活动的报名用户
    userz=User.query.join(AU).join(Activity).filter(Activity.id==id).all()
    user=[]
    for users in userz:
        user.append(users.username)
    # 获取系统活动的签到用户
    userz2 = User.query.join(AU).filter(and_(AU.activityid == id,AU.type==1)).all()
    user2=[]
    for users2 in userz2:
        user2.append(users2.username)
    # 返回活动名、活动类别、活动类型、开始时间、结束时间、活动内容、用户组
    da={'name':activity.name,'typeuser':activity.typeuser,'type':activity.type,'stoptime':str(activity.stoptime),'begintime':str(activity.begintime),'endtime':str(activity.endtime),'main':activity.main,'user':user,'user2':user2}
    return Response(json.dumps(da), mimetype='application/json')

#更新系统活动信息
@main.route('/updatesysactivity',methods=['GET','POST'])
def updatesysactivity():
    # 获取系统活动的活动名、活动类型、开始时间、结束时间、报名截止时间、活动内容
    if request.method == 'GET':
        id=request.args.get('id')
        name = request.args.get('name')
        type = request.args.get('type')
        begintime = request.args.get('begintime')
        endtime = request.args.get('endtime')
        stoptime = request.args.get('stoptime')
        main = request.args.get('main')
    else:
        id = request.form.get('id')
        name = request.form.get('name')
        type = request.form.get('type')
        begintime = request.form.get('begintime')
        endtime = request.form.get('endtime')
        stoptime = request.form.get('stoptime')
        main = request.form.get('main')
    # 处理时间类型数据
    if begintime!=None:
        begintime = datetime.datetime.strptime(begintime, '%Y-%m-%d')
    if endtime!=None:
        endtime = datetime.datetime.strptime(endtime, '%Y-%m-%d')
    if stoptime!=None:
        stoptime = datetime.datetime.strptime(stoptime, '%Y-%m-%d')
    user=session.get('user')
    userid=user['userid']
    # 修改活动及存表
    activity=Activity.query.filter(Activity.id==id).all()[0]
    if name!=None:
        activity.name=name
    if type!=None:
        activity.type=type
    if begintime!=None:
        activity.begintime=begintime
    if endtime!=None:
        activity.endtime=endtime
    if stoptime!=None:
        activity.stoptime=stoptime
    if main!=None:
        activity.main=main
    db.session.add(activity)
    db.session.commit()
    user2 = User.query.filter(User.id == userid).all()[0]
    user2.updatetime = activity.updatetime
    db.session.add(user2)
    db.session.commit()
    return Response(json.dumps({'status': True}), mimetype='application/json')

#删除系统活动
@main.route('/deletesysactivity',methods=['GET','POST'])
def deletesysactivity():
    if request.method == 'GET':
        id=request.args.get('id')
    else:
        id = request.form.get('id')
    # 修改活动及存表
    activity = Activity.query.filter(Activity.id == id).all()[0]
    activity.status=3#删除
    db.session.add(activity)
    db.session.commit()
    return Response(json.dumps({'status': True}), mimetype='application/json')

#生成报名表
@main.route('/xlsxsysactivity',methods=['GET','POST'])
def xlsxsysactivity():
    #根据活动id查找系统活动
    if request.method == "GET":
        id = request.args.get('id')
    else:
        id = request.form.get('id')
        #id = request.json.get('id')
    activity=Activity.query.filter(Activity.id==id).all()[0]
    # 获取系统活动的报名用户
    userz = User.query.join(AU).join(Activity).filter(Activity.id == id).all()
    user=[]
    for users in userz:
        user.append(users.username)
    # 创建存储地址data文件夹
    file_dir = os.path.join('data')
    if not os.path.exists(file_dir):
        os.makedirs(file_dir)
    #创建存储地址data\sysactivity文件夹
    file_dir = os.path.join('data\\sysactivity')
    if not os.path.exists(file_dir):
        os.makedirs(file_dir)
    #创建Excel表存储地址
    file_new_dir=os.path.join('data\\sysactivity\\'+str(id))
    if not os.path.exists(file_new_dir):
        os.makedirs(file_new_dir)
    #创建Excel表
    excelTabel = xlwt.Workbook()  # 创建excel对象
    begintime=str(activity.begintime).split('-')
    begintime=begintime[0]+'年'+begintime[1]+'月'+begintime[2].split(' ')[0]+'日'
    name=str(begintime+activity.name+"活动签到表")
    sheet1 = excelTabel.add_sheet(name, cell_overwrite_ok=True)
    #填写内容
    alignment = xlwt.Alignment()  # Create Alignment  创建对齐
    alignment.horz = xlwt.Alignment.HORZ_CENTER  # May be: 标准化：HORZ_GENERAL, 左对齐：HORZ_LEFT, 水平对齐居中：HORZ_CENTER, 右对齐：HORZ_RIGHT, 填充：HORZ_FILLED, HORZ_JUSTIFIED, HORZ_CENTER_ACROSS_SEL, HORZ_DISTRIBUTED
    alignment.vert = xlwt.Alignment.VERT_CENTER  # May be: 顶部对齐：VERT_TOP, 垂直居中：VERT_CENTER, 底部对齐：VERT_BOTTOM, VERT_JUSTIFIED, VERT_DISTRIBUTED
    style = xlwt.XFStyle()  # Create Style 创建样式
    style.alignment = alignment  # Add Alignment to Style  为样式添加对齐
    sheet1.write_merge(0,0,0,2,name,style)
    sheet1.write(1,0,"报名单位编号")
    sheet1.write(1,1,"活动报名单位")
    sheet1.write(1, 2, "签到")
    for i in range(len(user)):
        sheet1.write(i + 2, 0, i+1)
        sheet1.write(i+2, 1, str(user[i]))
    #以时间戳为Excel文件名
    timestamp=str(time.mktime(time.strptime(str(activity.updatetime), "%Y-%m-%d %H:%M:%S")))
    excelTabel.save('data\\sysactivity\\'+str(id)+'\\'+name+'.xlsx')
    # 获取文件名及文件绝对路径并将文件上传给前端
    filename = name+'.xlsx'
    file1=str(os.path.abspath(__file__))
    filed=file1.split('app')[0]
    directory = filed+'data\\sysactivity\\'+str(id)+'\\'
    return send_file(directory+filename, mimetype=str(mimetypes.guess_type(filename)[0]),attachment_filename=filename.encode('utf-8').decode('latin1'), as_attachment=True)

#获取本机ip地址
def get_host_ip():
    try:
        s=socket.socket(socket.AF_INET,socket.SOCK_DGRAM)
        s.connect(('8.8.8.8',80))
        ip=s.getsockname()[0]
    finally:
        s.close()
    return ip

#获取本机ip地址
def get_host_ip():
    try:
        s=socket.socket(socket.AF_INET,socket.SOCK_DGRAM)
        s.connect(('8.8.8.8',80))
        ip=s.getsockname()[0]
    finally:
        s.close()
    return ip

#生成二维码
@main.route('/ewmsysactivity',methods=['GET','POST'])
def ewmsysactivity():
    # 根据活动id查找系统活动
    if request.method == "GET":
        id = request.args.get('id')
    else:
        id = request.form.get('id')
        #id = request.json.get('id')
    activity = Activity.query.filter(Activity.id == id).all()[0]
    # 创建存储地址data文件夹
    file_dir = os.path.join('data')
    if not os.path.exists(file_dir):
        os.makedirs(file_dir)
    # 创建存储地址data\sysactivity文件夹
    file_dir = os.path.join('data\\sysactivity')
    if not os.path.exists(file_dir):
        os.makedirs(file_dir)
    # 创建二维码图片存储地址
    file_new_dir = os.path.join('data\\sysactivity\\' + str(id))
    if not os.path.exists(file_new_dir):
        os.makedirs(file_new_dir)
    #生成二维码
    qr = qrcode.QRCode(
        version=5,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )
    URL=get_host_ip()#获取本机ip地址
    url=URL+'/useractivitysign/'+id
    qr.add_data(url)
    qr.make(fit=True)
    img = qr.make_image()
    #以时间戳为文件名
    timestamp = str(time.mktime(time.strptime(str(activity.updatetime), "%Y-%m-%d %H:%M:%S")))
    filename = timestamp+'.png'
    img.save('data\\sysactivity\\'+str(id)+'\\'+filename)
    # 获取文件名及文件绝对路径并将文件上传给前端
    file1 = str(os.path.abspath(__file__))
    filed = file1.split('app')[0]
    directory = filed + 'data\\sysactivity\\' + str(id) + '\\'
    return send_file(directory + filename, mimetype=str(mimetypes.guess_type(filename)[0]),attachment_filename=filename, as_attachment=True)

#Web端总体获取需要签到的用户
@main.route('/websignuser',methods=['GET','POST'])
def websignuser():
    # 根据活动id查找系统活动
    if request.method == "GET":
        activityid = request.args.get('activityid')
    else:
        activityid = request.form.get('activityid')
        #activityid = request.json.get('activityid')
    au=AU.query.filter(AU.activityid==activityid).all()
    userz=[]
    for a in au:
        user=User.query.filter(User.id==a.userid).all()[0]
        userz.append({'name':user.name,'username':user.username,'userid':user.id})
    return Response(json.dumps({'userz': userz}), mimetype='application/json')

#Web端总体签到
@main.route('/websign',methods=['GET','POST'])
def websign():
    # 获取前端数据
    if request.method == "GET":
        activityid = request.args.get('activityid')
    else:
        #activityid = request.json.get('activityid')
        activityid=request.form.get('activityid')
    userz=request.values.getlist('userz[]')
    # 获取客户端ip地址
    ip = request.remote_addr
    for user in userz:
        au=AU.query.filter(and_(AU.activityid==activityid,AU.userid==user)).all()[0]
        au.type=1
        au.ip=ip
        db.session.add(au)
        db.session.commit()
    return Response(json.dumps({'status': True}), mimetype='application/json')

@main.route('/cs6',methods=['GET','POST'])
def cs():
    return render_template('cs6.html')