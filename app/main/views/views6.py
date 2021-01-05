from flask import request,jsonify,g
from app.main import main
from app.models.models import User,Activity,AD,Data
from werkzeug.utils import secure_filename
from app import db
import os
import base64,datetime,time

@main.after_app_request
def after_request(response):
    response.headers['Access-Control-Allow-Origin'] = '*'
    response.headers['Access-Control-Allow-Methods'] = 'PUT,GET,POST,DELETE'
    response.headers['Access-Control-Allow-Headers'] = 'Content-Type,Authorization'
    return response

def create_dir(s):
    file_dir = os.path.join(s)
    if not os.path.exists(file_dir):
        os.makedirs(file_dir)
    return file_dir

@main.route('/wxaddactivity',methods=['POST'])
def wxaddactivity():
    if request.method == "GET":
        name = request.args.get('name')
        begintime = request.args.get('begintime')
        endtime = request.args.get('endtime')
        main = request.args.get('main')
        type = request.args.get('type')
        username = request.args.get('username')
    else:
        name = request.form.get('name')
        begintime = request.form.get('begintime')
        endtime = request.form.get('endtime')
        main = request.form.get('main')
        type = request.form.get('type')
        username = request.form.get('username')
    by = str(begintime).split('年')[0]
    bm = str(begintime).split('年')[1].split('月')[0]
    bd = str(begintime).split('年')[1].split('月')[1].split('日')[0]
    bH = str(begintime).split('年')[1].split('月')[1].split('日')[1].split('时')[0]
    bM = str(begintime).split('年')[1].split('月')[1].split('日')[1].split('时')[1].split('分')[0]
    begintime2 = by + "-" + bm + "-" + bd + " " + bH + ":" + bM + ":00"
    begintime = datetime.datetime.strptime(begintime2, '%Y-%m-%d %H:%M:%S')
    ey = str(endtime).split('年')[0]
    em = str(endtime).split('年')[1].split('月')[0]
    ed = str(endtime).split('年')[1].split('月')[1].split('日')[0]
    eH = str(endtime).split('年')[1].split('月')[1].split('日')[1].split('时')[0]
    eM = str(endtime).split('年')[1].split('月')[1].split('日')[1].split('时')[1].split('分')[0]
    endtime2 = ey + "-" + em + "-" + ed + " " + eH + ":" + eM + ":00"
    endtime = datetime.datetime.strptime(endtime2, '%Y-%m-%d %H:%M:%S')
    cxtime = endtime - begintime
    user = User.query.filter(User.username == username).all()[0]
    userid = user.id
    activity = Activity(name=name, begintime=begintime, endtime=endtime, cxtime=cxtime, main=main, type=type,userid=userid)
    db.session.add(activity)
    db.session.commit()
    return jsonify({"activityid":activity.id})

@main.route('/wxupdate',methods=['POST'], strict_slashes=False)
def wxupdate():
    activityid=request.form.get('activityid')
    filetype = request.form.get('filetype')
    i=request.form.get('i')
    activityid=int(activityid)
    i=int(i)
    activity=Activity.query.filter(Activity.id==activityid).all()[0]
    file_dir = {}
    file_dir['base'] = create_dir('data')
    file_dir['video'] = create_dir('data\\video')
    file_dir['music'] = create_dir('data\music')
    file_dir['image'] = create_dir('data\image')
    f = request.files['myfile']  # 从表单的file字段获取文件，myfile为该表单的name值
    if f:  # 判断是否是允许上传的文件类型
        k=i+1
        filename = secure_filename(f.filename)
        ext = filename.rsplit('.', 1)[1]  # 获取文件后缀
        new_filename = str(activity.userid) + "_" + str(activity.id) + "_" + str(k) + '.' + ext  # 修改了上传的文件名
        f.save(os.path.join(file_dir[filetype], new_filename))  # 保存文件到目录
        file_data = 'data\\' + filetype + "\\" + new_filename
        data = Data(type=filetype, data=file_data)
        db.session.add(data)
        db.session.commit()
        activity.datas.append(data)
        db.session.add(activity)
        db.session.commit()
        user = User.query.filter(User.id == activity.userid).all()[0]
        user.updatetime = activity.uptime
        db.session.add(user)
        db.session.commit()
        bf = bytes(new_filename, encoding="utf8")
        token = base64.b64encode(bf)
        return jsonify({"errno": 0, "errmsg": "上传成功", "token": str(token, encoding="utf-8"),"activityid":activity.id})
    else:
        return jsonify({"errno": 1001, "errmsg": "上传失败"})
