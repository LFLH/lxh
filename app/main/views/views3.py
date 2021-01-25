#/manageactivity的后端API
from flask import request,jsonify,session,redirect,Response,send_from_directory,abort,make_response,send_file
from app.main import main
from app.models.models import User,Activity,AD,Data,AU
from app import db
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

#列表显示活动
@main.route('/searchactivity',methods=['GET', 'POST'])
def searchactivity():
    if request.method == "GET":
        page = request.args.get('page')#当前页
        per_page=request.args.get('per_page')#平均页数
    else:
        page = request.json.get('page')
        per_page = request.json.get('per_page')
    page = int(page)
    per_page = int(per_page)
    #获取未删除活动倒叙
    activity = Activity.query.order_by(-Activity.updatetime).paginate(page, per_page, error_out=False)
    items = activity.items
    item = []
    count = (int(page) - 1) * int(per_page)
    for i in range(len(items)):
        if items[i].typeuser=='自主':
            user=User.query.filter(User,id==items[i].userid).all()[0]
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
        id = request.json.get('id')
    activity=Activity.query.filter(Activity.id==id).all()[0]
    #获取自主活动的文件名
    data=activity.datas
    filedata={'video':[],'music':[],'image':[],'pdf':[],'word':[]}
    for datai in data:
        dataz={'name':datai.name,'path':datai.path,'newname':datai.newname}
        filedata[datai.type].append(dataz)
    #返回活动名、活动类别、活动类型、开始时间、结束时间、活动内容、视频、音频、图片、pdf、word
    da={'name':activity.name,'typeuser':activity.typeuser,'type':activity.type,'begintime':str(activity.begintime),'endtime':str(activity.endtime),'main':activity.main,'video':filedata['video'],'music':filedata['music'],'image':filedata['image'],'pdf':filedata['pdf'],'word':filedata['word']}
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
        id = request.json.get('id')
    activity=Activity.query.filter(Activity.id==id).all()[0]
    # 获取系统活动的报名用户
    userz=User.query.join(AU).join(Activity).filter(Activity.id==id).all()
    user=[]
    for users in userz:
        user.append(users.username)
    # 返回活动名、活动类别、活动类型、开始时间、结束时间、活动内容、用户组
    da={'name':activity.name,'typeuser':activity.typeuser,'type':activity.type,'begintime':str(activity.begintime),'endtime':str(activity.endtime),'main':activity.main,'user':user}
    return Response(json.dumps(da), mimetype='application/json')

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
    begintime = datetime.datetime.strptime(begintime, '%Y-%m-%d')
    endtime = datetime.datetime.strptime(endtime, '%Y-%m-%d')
    stoptime = datetime.datetime.strptime(stoptime, '%Y-%m-%d')
    user=session.get('user')
    userid=user['userid']
    # 修改活动及存表
    activity=Activity.query.filter(Activity.id==id).all()[0]
    activity.name=name
    activity.type=type
    activity.begintime=begintime
    activity.endtime=endtime
    activity.stoptime=stoptime
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
        id = request.json.get('id')
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
    sheet1.write_merge(0,0,0,2,name)
    sheet1.write(1,0,"报名单位编号")
    sheet1.write(1,1,"活动报名单位")
    sheet1.write(1, 2, "签到")
    for i in range(len(user)):
        sheet1.write(i + 2, 0, i+1)
        sheet1.write(i+2, 1, str(user[i]))
    #以时间戳为Excel文件名
    timestamp=str(time.mktime(time.strptime(str(activity.updatetime), "%Y-%m-%d %H:%M:%S")))
    excelTabel.save('data\\sysactivity\\'+str(id)+'\\'+timestamp+'.xlsx')
    # 获取文件名及文件绝对路径并将文件上传给前端
    filename = timestamp+'.xlsx'
    file1=str(os.path.abspath(__file__))
    filed=file1.split('app\main\\views\\views3.py')[0]
    directory = filed+'data\\sysactivity\\'+str(id)+'\\'
    return send_file(directory+filename, mimetype=str(mimetypes.guess_type(filename)[0]),attachment_filename=filename, as_attachment=True)

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
        id = request.json.get('id')
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
    filed = file1.split('app\main\\views\\views3.py')[0]
    directory = filed + 'data\\sysactivity\\' + str(id) + '\\'
    return send_file(directory + filename, mimetype=str(mimetypes.guess_type(filename)[0]),attachment_filename=filename, as_attachment=True)