from flask import request, jsonify, Response, session, redirect
from app.main import main
from app.models.models import User, Activity, AD, Data
from werkzeug.utils import secure_filename
from app import db
import os, json, datetime, time


@main.after_app_request
def after_request(response):
    response.headers['Access-Control-Allow-Origin'] = '*'
    response.headers['Access-Control-Allow-Methods'] = 'PUT,GET,POST,DELETE'
    response.headers['Access-Control-Allow-Headers'] = 'Content-Type,Authorization'
    return response


def panduan(ext):
    video = ['asf', 'asx', 'dvr-ms', 'wm', 'wmp', 'wmv', 'ra', 'ram', 'rm', 'rmvb', 'mov', 'qt', 'f4v', 'flv', 'hlv',
             'swf', 'ifo', 'vob', 'dat', 'm1v', 'm2p', 'm2t', 'm2ts', 'm2v', 'm4b', 'm4p', 'm4v', 'mp2v', 'mp4', 'mpe',
             'mpeg', 'mpeg4', 'mpg', 'mpv2', 'pva', 'tp', 'ts', 'mpeg1', 'mpeg2', '3g2', '3gp', '3gp2', '3gpp', '2634',
             'amv', 'avi', 'bik', 'divx', 'dpg', 'evo', 'h264', 'ivm', 'k3g', 'mkv', 'mod', 'mp4v', 'mts', 'nsr', 'nsv',
             'ogm', 'ogv', 'pfv', 'pmf', 'pmp', 'pss', 'scm', 'skm', 'tod', 'tpr', 'trp', 'vp6', 'vp7', 'webm', 'wtv',
             'mp41', 'dv', 'mtv', 'mxf', 'vro', 'vdat']
    music = ['ape', 'cda', 'flac', 'tta', 'wma', 'wav', 'wv', 'aac', 'aif', 'aiff', 'amr', 'dts', 'dtshd', 'm1a', 'm2a',
             'm4a', 'm4r', 'mid', 'midi', 'mka', 'mp2', 'mp3', 'mp5', 'mpa', 'mpc', 'ogg', 'rmi', 'tak', 'ogx', 'au',
             'ac3', 'mp1', 'opus', 'dsf', 'dff']
    image = ['bmp', 'pcx', 'png', 'gif', 'jpeg', 'tiff', 'cgm', 'dxf', 'cdr', 'wmf', 'eps', 'emf', 'pict', 'jpg']
    word = ['doc', 'docx']
    pdf = ['pdf']
    if ext in video:
        type = 'video'
    elif ext in music:
        type = 'music'
    elif ext in image:
        type = 'image'
    elif ext in word:
        type = 'word'
    elif ext in pdf:
        type = 'pdf'
    else:
        type = 'error'
    return type


def create_dir(s):
    file_dir = os.path.join(s)
    if not os.path.exists(file_dir):
        os.makedirs(file_dir)
    return file_dir


@main.route('/addactivity', methods=['GET', 'POST'])
def addactivity():
    if request.method == "GET":
        name = request.args.get('name')
        begintime = request.args.get('begintime')
        endtime = request.args.get('endtime')
        main = request.args.get('main')
        type = request.args.get('type')
    else:
        '''
        name = request.json.get('name')
        begintime = request.json.get('begintime')
        endtime = request.json.get('endtime')
        main = request.json.get('main')
        type = request.json.get('type')
        '''
        name = request.form.get('name')
        begintime = request.form.get('begintime')
        endtime = request.form.get('endtime')
        main = request.form.get('main')
        type = request.form.get('type')
    username = session.get('username')
    begintime = datetime.datetime.strptime(begintime, '%Y-%m-%d')
    endtime = datetime.datetime.strptime(endtime, '%Y-%m-%d')
    cxtime = endtime - begintime
    user = User.query.filter(User.username == username).all()[0]
    userid = user.id
    activity = Activity(name=name, begintime=begintime, endtime=endtime, cxtime=cxtime, main=main, type=type,
                        userid=userid)
    db.session.add(activity)
    db.session.commit()
    user.updatetime = activity.uptime
    db.session.add(user)
    db.session.commit()
    session["activityid"] = activity.id
    return Response(json.dumps({'status': True}), mimetype='application/json')


@main.route('/addactivitydata', methods=['GET', 'POST'])
def addactivitydata():
    time.sleep(30)
    username = session.get('username')
    user = User.query.filter(User.username == username).all()[0]
    userid = user.id
    # activity=Activity.query.filter(Activity.userid==userid).order_by(-Activity.uptime).all()[0]#修改
    activityid = session.get("activityid")
    activity = Activity.query.filter(Activity.id == activityid).all()[0]
    upload_files = request.files.getlist('file')
    file_dir = {}
    file_dir['base'] = create_dir('data')
    file_dir['video'] = create_dir('data\\video')
    file_dir['music'] = create_dir('data\music')
    file_dir['image'] = create_dir('data\image')
    for file in upload_files:
        filename = secure_filename(file.filename)
        ext = filename.rsplit('.')
        ext = ext[len(ext) - 1].lower()
        type = panduan(ext)
        if type == 'error':
            activity.status = "delete"
            db.session.add(activity)
            db.session.commit()
            session.pop('activityid', None)
            return redirect('/userupdata?status=False')
    for i in range(len(upload_files)):
        file = upload_files[i]
        filename = secure_filename(file.filename)
        ext = filename.rsplit('.')
        ext = ext[len(ext) - 1].lower()  # 获取文件后缀
        type = panduan(ext)
        new_filename = str(userid) + "_" + str(activity.id) + "_" + str(i) + '.' + ext  # 修改了上传的文件名
        file.save(os.path.join(file_dir[type], new_filename))  # 保存文件到目录
        file_data = 'data\\' + type + "\\" + new_filename
        data = Data(type=type, data=file_data)
        db.session.add(data)
        db.session.commit()
        activity.datas.append(data)
    db.session.add(activity)
    db.session.commit()
    session.pop("activityid", None)
    # return Response(json.dumps({'status':True}), mimetype='application/json')
    return redirect('/userupdata?status=True')


@main.route('/addactivitycs', methods=['GET', 'POST'])
def addactivitycs():
    name = request.args.get('name')
    begintime = request.args.get('begintime')
    endtime = request.args.get('endtime')
    main = request.args.get('main')
    type = request.args.get('type')
    username = session.get('username')
    begintime = datetime.datetime.strptime(begintime, '%Y-%m-%d')
    endtime = datetime.datetime.strptime(endtime, '%Y-%m-%d')
    cxtime = endtime - begintime
    user = User.query.filter(User.username == username).all()[0]
    userid = user.id
    activity = Activity(name=name, begintime=begintime, endtime=endtime, cxtime=cxtime, main=main, type=type,
                        userid=userid)
    db.session.add(activity)
    db.session.commit()
    user.updatetime = activity.uptime
    db.session.add(user)
    db.session.commit()
    filelist = ['video', 'music', 'image', 'pdf', 'word']
    upload_files = {}
    file_dir = {}
    file_dir['base'] = create_dir('data')
    filedata = []
    for i in range(len(filelist)):
        filedata.append([])
        upload_files[filelist[i]] = request.files.getlist(filelist[i])
        file_dir[filelist[i]] = create_dir('data\\' + filelist[i])
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
                activity.status = "delete"
                db.session.add(activity)
                db.session.commit()
                return Response(json.dumps({'status': False}), mimetype='application/json')
    for i in range(len(filelist)):
        upload_file = upload_files[filelist[i]]
        for j in range(len(upload_file)):
            file = upload_file[j]
            filename = secure_filename(file.filename)
            ext = filename.rsplit('.')
            ext = ext[len(ext) - 1].lower()  # 获取文件后缀
            type = filelist[i]
            new_filename = str(userid) + "_" + str(activity.id) + "_" + str(j + 1) + '.' + ext  # 修改了上传的文件名
            file.save(os.path.join(file_dir[type], new_filename))  # 保存文件到目录
            file_data = 'data\\' + type + "\\" + new_filename
            f = open(file_data, 'wb')
            f.write(filedata[i][j])
            f.close()
            data = Data(type=type, data=file_data)
            db.session.add(data)
            db.session.commit()
            activity.datas.append(data)
    db.session.add(activity)
    db.session.commit()
    # return redirect('/userupdata?status=True')
    return Response(json.dumps({'status': True}), mimetype='application/json')


@main.route('/showactivity', methods=['GET', 'POST'])
def showactivity():
    if request.method == "GET":
        page = request.args.get('page')  # 当前页
        per_page = request.args.get('per_page')  # 平均页数
    else:
        page = request.json.get('page')
        per_page = request.json.get('per_page')
    username = session.get("username")
    page = int(page)
    per_page = int(per_page)
    activity = Activity.query.join(User).filter(Activity.userid == User.id).filter(Activity.status != "delete").filter(
        User.username == username).order_by(-Activity.uptime).paginate(page, per_page, error_out=False)
    items = activity.items
    item = []
    count = (int(page) - 1) * int(per_page)
    for i in range(len(items)):
        itemss = {'number': count + i + 1, 'id': items[i].id, 'activityname': items[i].name, 'type': items[i].type,
                  'begintime': str(items[i].begintime), "endtime": str(items[i].endtime), "main": items[i].main}
        item.append(itemss)
    data = {'zpage': activity.pages, 'total': activity.total, 'dpage': activity.page, 'item': item}
    return Response(json.dumps(data), mimetype='application/json')
