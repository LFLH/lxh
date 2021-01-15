#/useractivity的后端API
from flask import request,jsonify,session,redirect,Response
from app.main import main
from app.models.models import User,Activity,AD,Data,Declare,UDeclare,Train,UTrain,Score,System
from app import db
import json,datetime,random,string,os
from sqlalchemy import or_,and_
from werkzeug.utils import secure_filename

@main.after_app_request
def after_request(response):
    response.headers['Access-Control-Allow-Origin'] = '*'
    response.headers['Access-Control-Allow-Methods'] = 'PUT,GET,POST,DELETE'
    response.headers['Access-Control-Allow-Headers'] = 'Content-Type,Authorization'
    return response

#列表显示自主活动信息
@main.route('/showactivity',methods=['GET', 'POST'])
def showactivity():
    if request.method == "GET":
        page = request.args.get('page')#当前页
        per_page=request.args.get('per_page')#平均页数
    else:
        page = request.json.get('page')
        per_page = request.json.get('per_page')
    user = session.get('user')
    userid = user['userid']
    #根据用户id获取自主活动
    page=int(page)
    per_page=int(per_page)
    activity = Activity.query.filter(Activity.userid == userid).filter(Activity.status!=3).order_by(-Activity.updatetime).paginate(page, per_page, error_out=False)
    items = activity.items
    item = []
    count = (int(page) - 1) * int(per_page)
    for i in range(len(items)):
        #返回活动名、活动类型、开始时间、结束时间、活动内容、状态
        itemss = {'number': count + i + 1, 'id': items[i].id, 'activityname': items[i].name,'type':items[i].type,
                  'begintime': str(items[i].begintime),"endtime":str(items[i].endtime),"main":items[i].main,"status":items[i].status}
        item.append(itemss)
    # 返回总页数、活动总数、当前页、活动集合
    data = {'zpage': activity.pages, 'total': activity.total, 'dpage': activity.page, 'item': item}
    return Response(json.dumps(data), mimetype='application/json')

#显示自主活动详细信息
@main.route('/detailactivity',methods=['GET','POST'])
def detailactivity():
    # 根据活动id查找自主活动
    if request.method == "GET":
        id = request.args.get('id')
    else:
        id = request.json.get('id')
    activity = Activity.query.filter(Activity.id == id).all()[0]
    # 获取自主活动的文件名
    data = activity.datas
    filedata = {'video': [], 'music': [], 'image': [], 'pdf': [], 'word': []}
    for datai in data:
        filedata[datai.type].append(datai.name)
    # 返回活动名、活动类别、活动类型、开始时间、结束时间、活动内容、视频、音频、图片、pdf、word
    da = {'name': activity.name, 'typeuser': activity.typeuser, 'type': activity.type,
          'begintime': str(activity.begintime), 'endtime': str(activity.endtime), 'main': activity.main,
          'video': filedata['video'], 'music': filedata['music'], 'image': filedata['image'], 'pdf': filedata['pdf'],
          'word': filedata['word']}
    return Response(json.dumps(da), mimetype='application/json')

#判断上传文件类型
def panduan(ext):
    video=['asf','asx','dvr-ms','wm','wmp','wmv','ra','ram','rm','rmvb','mov','qt','f4v','flv','hlv','swf','ifo','vob','dat','m1v','m2p','m2t','m2ts','m2v','m4b','m4p','m4v','mp2v','mp4','mpe','mpeg','mpeg4','mpg','mpv2','pva','tp','ts','mpeg1','mpeg2','3g2','3gp','3gp2','3gpp','2634','amv','avi','bik','divx','dpg','evo','h264','ivm','k3g','mkv','mod','mp4v','mts','nsr','nsv','ogm','ogv','pfv','pmf','pmp','pss','scm','skm','tod','tpr','trp','vp6','vp7','webm','wtv','mp41','dv','mtv','mxf','vro','vdat']
    music=['ape','cda','flac','tta','wma','wav','wv','aac','aif','aiff','amr','dts','dtshd','m1a','m2a','m4a','m4r','mid','midi','mka','mp2','mp3','mp5','mpa','mpc','ogg','rmi','tak','ogx','au','ac3','mp1','opus','dsf','dff']
    image=['bmp','pcx','png','gif','jpeg','tiff','cgm','dxf','cdr','wmf','eps','emf','pict','jpg']
    word=['doc','docx']
    pdf=['pdf']
    if ext in video:
        type='video'
    elif ext in music:
        type='music'
    elif ext in image:
        type='image'
    elif ext in word:
        type='word'
    elif ext in pdf:
        type='pdf'
    else:
        type='error'
    return type

#创建文件夹
def create_dir(s):
    file_dir = os.path.join(s)
    if not os.path.exists(file_dir):
        os.makedirs(file_dir)
    return file_dir

#修改自主活动信息
@main.route('/updateactivity',methods=['GET','POST'])
def updateactivity():
    # 创建文件夹
    filelist = ['video', 'music', 'image', 'pdf', 'word']
    upload_files = {}
    file_dir = {}
    file_dir['base'] = create_dir('data')
    filedata = []
    for i in range(len(filelist)):
        filedata.append([])
        upload_files[filelist[i]] = request.files.getlist(filelist[i])
        file_dir[filelist[i]] = create_dir('data\\' + filelist[i])
    # 检查文件类型及大小
    for i in range(len(filelist)):
        for file in upload_files[filelist[i]]:
            filename = secure_filename(file.filename)
            ext = filename.rsplit('.')
            ext = ext[len(ext) - 1].lower()
            type = panduan(ext)
            filedata[i].append(file.read())
            j = len(filedata[i]) - 1
            size = int(len(filedata[i][j]) / 1024 / 1024)
            if type != filelist[i] or size > 100:
                return Response(json.dumps({'status': False}), mimetype='application/json')
    id=request.args.get('id')
    name = request.args.get('name')
    begintime = request.args.get('begintime')
    endtime = request.args.get('endtime')
    main = request.args.get('main')
    type = request.args.get('type')
    begintime = datetime.datetime.strptime(begintime, '%Y-%m-%d')
    endtime = datetime.datetime.strptime(endtime, '%Y-%m-%d')
    user = session.get('user')
    userid = user['userid']
    user = User.query.filter(User.id == userid).all()[0]
    # 根据活动id查找自主活动
    activity = Activity.query.filter(Activity.id==id).all()[0]
    #修改活动信息
    activity.name=name
    activity.type=type
    activity.begintime=begintime
    activity.endtime=endtime
    activity.main=main
    activity.updatetime=datetime.datetime.now()
    #移除活动中的文件
    datas=activity.datas
    length=len(datas)
    for i in range(length):
        activity.datas.remove(datas[length-i-1])
    db.session.add(activity)
    db.session.commit()
    #修改用户操作时间
    user.updatetime = activity.updatetime
    db.session.add(user)
    db.session.commit()
    #保存文件
    for i in range(len(filelist)):
        upload_file=upload_files[filelist[i]]
        for j in range(len(upload_file)):
            file=upload_file[j]
            filename = secure_filename(file.filename)
            ext = filename.rsplit('.')
            ext = ext[len(ext) - 1].lower()  # 获取文件后缀
            type=filelist[i]
            new_filename = str(userid) + "_" + str(activity.id) + "_" + str(j+1) + '.' + ext  # 修改了上传的文件名
            file.save(os.path.join(file_dir[type], new_filename)) # 保存文件到目录
            file_data = 'data\\' + type + "\\" + new_filename
            f=open(file_data,'wb')
            f.write(filedata[i][j])
            f.close()
            data = Data(name = file.filename,type=filelist[i],path=file_data,newname=new_filename)
            db.session.add(data)
            db.session.commit()
            activity.datas.append(data)
    db.session.add(activity)
    db.session.commit()
    return Response(json.dumps({'status': True}), mimetype='application/json')

#删除自主活动
@main.route('/deleteactivity',methods=['GET', 'POST'])
def deleteactivity():
    if request.method == "GET":
        id = request.args.get('id')
        page = request.args.get('page')  # 当前页
        per_page = request.args.get('per_page')  # 平均页数
    else:
        id = request.json.get('id')
        page = request.json.get('page')  # 当前页
        per_page = request.json.get('per_page')  # 平均页数
    page = int(page)
    per_page = int(per_page)
    #根据活动id删除活动
    activity = Activity.query.filter(Activity.id == id).all()[0]
    activity.status=3
    db.session.add(activity)
    db.session.commit()
    #查找用户的活动
    userid=session.get('user')['userid']
    activity2 = Activity.query.filter(Activity.userid == userid).filter(Activity.status!=3).order_by(-Activity.updatetime).paginate(page, per_page,error_out=False)
    items = activity2.items
    item = []
    count = (int(page) - 1) * int(per_page)
    for i in range(len(items)):
        itemss = {'number': count + i + 1, 'id': items[i].id, 'activityname': items[i].name,
                  'type': items[i].type,'begintime': str(items[i].begintime), "endtime": str(items[i].endtime), 'status': items[i].status}
        item.append(itemss)
    # 返回总页数、活动总数、当前页、活动集合
    data = {'zpage': activity2.pages, 'total': activity2.total, 'dpage': activity2.page, 'item': item}
    #data = sadetail(page, per_page)
    return Response(json.dumps(data), mimetype='application/json')