from flask import request,jsonify,make_response,Response,session
from app.main import main
from app.models.models import User,Activity,AD,Data
from app import db
import os,mimetypes,json

@main.after_app_request
def after_request(response):
    response.headers['Access-Control-Allow-Origin'] = '*'
    response.headers['Access-Control-Allow-Methods'] = 'PUT,GET,POST,DELETE'
    response.headers['Access-Control-Allow-Headers'] = 'Content-Type,Authorization'
    return response

def sadetail(page,per_page,username,type,time):
    k = 0
    if username != None:
        k = k + 4
    if type != None:
        k = k + 2
    if time != None:
        k = k + 1
    activity=Activity.query.filter(Activity.status!="delete")
    if k == 0:
        activity = activity.order_by(Activity.uptime).paginate(page, per_page, error_out=False)
    if k == 1:
        activity = activity.filter(Activity.uptime < time).order_by(Activity.uptime).paginate(page, per_page,
                                                                                                    error_out=False)
    if k == 2:
        activity = activity.filter(Activity.type == type).order_by(Activity.uptime).paginate(page, per_page,
                                                                                                   error_out=False)
    if k == 3:
        activity = activity.filter(Activity.type == type).filter(Activity.uptime < time).order_by(
            Activity.uptime).paginate(page, per_page, error_out=False)
    if k == 4:
        activity = activity.join(User).filter(Activity.userid == User.id).filter(
            User.username == username).order_by(Activity.uptime).paginate(page, per_page, error_out=False)
    if k == 5:
        activity = activity.join(User).filter(Activity.userid == User.id).filter(
            User.username == username).filter(Activity.uptime < time).order_by(Activity.uptime).paginate(page, per_page,
                                                                                                         error_out=False)
    if k == 6:
        activity = activity.join(User).filter(Activity.userid == User.id).filter(
            User.username == username).filter(Activity.type == type).order_by(Activity.uptime).paginate(page, per_page,
                                                                                                        error_out=False)
    if k == 7:
        activity = activity.join(User).filter(Activity.userid == User.id).filter(
            User.username == username).filter(Activity.uptime < time).filter(Activity.type == type).order_by(
            Activity.uptime).paginate(page, per_page, error_out=False)
    items = activity.items
    item = []
    count = (int(page) - 1) * int(per_page)
    for i in range(len(items)):
        user=User.query.filter(User.id==items[i].userid).all()[0]
        itemss = {'number': count + i + 1, 'id': items[i].id, 'activityname': items[i].name,'type':items[i].type,
                  'begintime': str(items[i].begintime),"endtime":str(items[i].endtime),"main":items[i].main,"username":user.username}
        item.append(itemss)
    data = {'zpage': activity.pages, 'total': activity.total, 'dpage': activity.page, 'item': item}
    return data

def create_dir(s):
    file_dir = os.path.join(s)
    if not os.path.exists(file_dir):
        os.makedirs(file_dir)
    return file_dir

@main.route('/searchactivity',methods=['GET', 'POST'])
def searchactivity():
    if request.method == "GET":
        page = request.args.get('page')#当前页
        per_page=request.args.get('per_page')#平均页数
        #可能条件
        type=request.args.get('type')
        time=request.args.get('time')
        username = request.args.get('username')
    else:
        page = request.json.get('page')
        per_page = request.json.get('per_page')
        type = request.json.get('type')
        time = request.json.get('time')
        username = request.json.get('username')
    page = int(page)
    per_page = int(per_page)
    data=sadetail(page,per_page,username,type,time)
    return Response(json.dumps(data), mimetype='application/json')

@main.route('/detailactivity',methods=['GET', 'POST'])
def detailactivity():
    if request.method == "GET":
        id = request.args.get('id')
    else:
        id = request.json.get('id')
    activity=Activity.query.filter(Activity.id==id).all()[0]
    datas=activity.datas.all()
    user=User.query.filter(User.id==activity.userid).all()[0]
    item=[]
    for data in datas:
        dataa={'type':data.type,'data':data.data}
        item.append(dataa)
    da={'username':user.username,'name':activity.name,'begintime':activity.begintime,'endtime':activity.endtime,'cxtime':activity.cxtime,'uptime':activity.uptime,'main':activity.main,'type':activity.type,'datas':item}
    return Response(json.dumps(da), mimetype='application/json')

@main.route('/deleteactivity',methods=['GET', 'POST'])
def deleteactivity():
    if request.method == "GET":
        id = request.args.get('id')
        page = request.args.get('page')  # 当前页
        per_page = request.args.get('per_page')  # 平均页数
        # 可能条件
        type = request.args.get('type')
        time = request.args.get('time')
        username = request.args.get('username')
    else:
        id = request.json.get('id')
        page = request.json.get('page')  # 当前页
        per_page = request.json.get('per_page')  # 平均页数
        type = request.json.get('type')
        time = request.json.get('time')
        username=request.json.get('username')
    page = int(page)
    per_page = int(per_page)
    activity = Activity.query.filter(Activity.id == id).all()[0]
    activity.status="delete"
    db.session.add(activity)
    db.session.commit()
    data = sadetail(page, per_page, username, type, time)
    return Response(json.dumps(data), mimetype='application/json')

@main.route('/data/image/<string:filename>', methods=['GET'])
def image(filename):
    if request.method == 'GET':
        if filename is None:
            pass
        else:
            file_dir = create_dir('data\image')
            image_data = open(os.path.join(file_dir, filename), "rb").read()
            response = make_response(image_data)
            response.headers['Content-Type'] = str(mimetypes.guess_type(filename)[0])
            return response
    else:
        pass

@main.route('/data/music/<string:filename>', methods=['GET'])
def music(filename):
    def generate(filename):
        file_dir = create_dir('data\music')
        path = os.path.join(file_dir,filename)
        with open(path, 'rb') as fmp3:
            data = fmp3.read(1024)
            while data:
                yield data
                data = fmp3.read(1024)
    return Response(generate(filename), mimetype=str(mimetypes.guess_type(filename)[0]))

@main.route('/data/video/<string:filename>',methods=['GET'])
def video(filename):
    def generate(filename):
        file_dir = create_dir('data\\video')
        path = os.path.join(file_dir,filename)
        with open(path, 'rb') as fmp4:
            data = fmp4.read(1024)
            while data:
                yield data
                data = fmp4.read(1024)
    return Response(generate(filename), mimetype=str(mimetypes.guess_type(filename)[0]))