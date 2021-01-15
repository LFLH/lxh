#/usertrainregister的后端API
from flask import request,jsonify,session,redirect,Response
from app.main import main
from app.models.models import User,Activity,AD,Data,Declare,UDeclare,Train,UTrain,Score,System,AU,TUT
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

# 列表查看系统能力提升培训
@main.route('/searchsystrain',methods=['GET','POST'])
def searchsystrain():
    if request.method == "GET":
        page = request.args.get('page')#当前页
        per_page=request.args.get('per_page')#平均页数
    else:
        page = request.json.get('page')
        per_page = request.json.get('per_page')
    page=int(page)
    per_page=int(per_page)
    user = session.get('user')
    userid = user['userid']
    train = Train.query.order_by(-Train.endtime).paginate(page, per_page, error_out=False)
    items = train.items
    item = []
    count = (int(page) - 1) * int(per_page)
    for i in range(len(items)):
        if items[i].endtime<datetime.datetime.now():
            status=1
        else:
            tut=Train.query.join(TUT).join(UTrain).filter(and_(Train.id==items[i].id,UTrain.userid==userid)).count()
            if tut>0:
                status=1
            else:
                status=0
        # 返回培训名、开始时间、结束时间、状态
        itemss={'number': count + i + 1,'id':items[i].id,'name': items[i].name, 'begintime': str(items[i].begintime), 'endtime': str(items[i].endtime),'status':status}
        item.append(itemss)
    # 返回总页数、活动总数、当前页、活动集合
    data = {'zpage': train.pages, 'total': train.total, 'dpage': train.page, 'item': item}
    return Response(json.dumps(data), mimetype='application/json')

# 查看系统能力提升培训详细信息
@main.route('/detailsystrain', methods=['GET', 'POST'])
def detailsystrain():
    if request.method == 'GET':
        id = request.args.get('id')
    else:
        id = request.form.get('id')
    train = Train.query.filter_by(id=id).first()
    #返回培训名、内容、开始时间、结束时间
    result = {'name': train.name, 'main': train.main, 'begintime': str(train.begintime), 'endtime': str(train.endtime)}
    return Response(json.dumps(result), mimetype='application/json')

#判断上传文件类型
def panduan(ext):
    image=['bmp','pcx','png','gif','jpeg','tiff','cgm','dxf','cdr','wmf','eps','emf','pict','jpg']
    word=['doc','docx']
    pdf=['pdf']
    if ext in image:
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


#报名提交能力提升培训
@main.route('/bmsystrain',methods=['GET','POST'])
def bmsystrain():
    # 创建文件夹
    filelist = ['image', 'pdf', 'word']
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
    user = session.get('user')
    userid = user['userid']
    user = User.query.filter(User.id == userid).all()[0]
    # 创建用户申请
    utrain=UTrain(userid=userid)
    db.session.add(utrain)
    db.session.commit()
    # 修改用户操作时间
    user.updatetime = datetime.datetime.now()
    db.session.add(user)
    db.session.commit()
    # 保存文件
    for i in range(len(filelist)):
        upload_file = upload_files[filelist[i]]
        for j in range(len(upload_file)):
            file = upload_file[j]
            filename = secure_filename(file.filename)
            ext = filename.rsplit('.')
            ext = ext[len(ext) - 1].lower()  # 获取文件后缀
            type = filelist[i]
            new_filename = str(userid) + "_" + str(utrain.id) + "_" + str(j + 1) + '.' + ext  # 修改了上传的文件名
            file.save(os.path.join(file_dir[type], new_filename))  # 保存文件到目录
            file_data = 'data\\' + type + "\\" + new_filename
            f = open(file_data, 'wb')
            f.write(filedata[i][j])
            f.close()
            data = Data(name=file.filename, type=filelist[i], path=file_data, newname=new_filename)
            db.session.add(data)
            db.session.commit()
            utrain.datas.append(data)
    db.session.add(utrain)
    db.session.commit()
    # 连接培训和用户培训
    train=Train.query.filter(Train.id==id).all()[0]
    train.utrains.append(utrain)
    db.session.add(train)
    db.session.commit()
    return Response(json.dumps({'status': True}), mimetype='application/json')