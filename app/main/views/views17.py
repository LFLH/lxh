#/userndreport的后端API
from flask import request,jsonify,session,redirect,Response
from app.main import main
from app.models.models import User,Activity,AD,Data,Declare,UDeclare,Train,UTrain,Score,System,AU,Record
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


#提交年度报告
@main.route('/addndreport',methods=['GET','POST'])
def addndreport():
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
    name = request.args.get('name')
    user = session.get('user')
    userid = user['userid']
    user = User.query.filter(User.id == userid).all()[0]
    # 创建报告
    record = Record(userid=userid, name=name,type="年度")
    db.session.add(record)
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
            new_filename = str(userid) + "_" + str(record.id) + "_" + str(j + 1) + '.' + ext  # 修改了上传的文件名
            file.save(os.path.join(file_dir[type], new_filename))  # 保存文件到目录
            file_data = 'data\\' + type + "\\" + new_filename
            f = open(file_data, 'wb')
            f.write(filedata[i][j])
            f.close()
            data = Data(name=file.filename, type=filelist[i], path=file_data, newname=new_filename)
            db.session.add(data)
            db.session.commit()
            record.datas.append(data)
    db.session.add(record)
    db.session.commit()
    return Response(json.dumps({'status': True}), mimetype='application/json')
