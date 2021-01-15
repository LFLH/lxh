from flask import request,jsonify,make_response,Response,session
from app.main import main
from app.models.models import Activity,AD,Data
from app import db
import os,mimetypes,json

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
    activity = Activity.query.filter(Activity.status != 3).order_by(-Activity.updatetime).paginate(page, per_page, error_out=False)
    items = activity.items
    item = []
    count = (int(page) - 1) * int(per_page)
    for i in range(len(items)):
        itemss = {'number': count + i + 1, 'id': items[i].id, 'activityname': items[i].name, 'typeuser':items[i].typeuser,'type': items[i].type,
                  'begintime': str(items[i].begintime), "endtime": str(items[i].endtime),'status':items[i].status}
        item.append(itemss)
    data = {'zpage': activity.pages, 'total': activity.total, 'dpage': activity.page, 'item': item}
    return Response(json.dumps(data), mimetype='application/json')

@main.route('/detailuseractivity',methods=['GET', 'POST'])
def detailuseractivity():
    if request.method == "GET":
        id = request.args.get('id')
    else:
        id = request.json.get('id')
    activity=Activity.query.filter(Activity.id==id).all()[0]
    data=activity.datas
    filedata={'video':[],'music':[],'image':[],'pdf':[],'word':[]}
    for datai in data:
        filedata[datai.type].append(datai.name)
    da={'name':activity.name,'typeuser':activity.typeuser,'type':activity.type,'begintime':str(activity.begintime),'endtime':str(activity.endtime),'main':activity.main,'video':filedata['video'],'music':filedata['music'],'image':filedata['image'],'pdf':filedata['pdf'],'word':filedata['word']}
    return Response(json.dumps(da), mimetype='application/json')

@main.route('/detailsysactivity',methods=['GET','POST'])
def detailsysactivity():
    if request.method == "GET":
        id = request.args.get('id')
    else:
        id = request.json.get('id')
    activity=Activity.query.filter(Activity.id==id).all()[0]
    userz=activity.users
    user=[]
    for users in userz:
        user.append(users.username)
    da={'name':activity.name,'typeuser':activity.typeuser,'type':activity.type,'begintime':str(activity.begintime),'endtime':str(activity.endtime),'main':activity.main,'user':user}
    return Response(json.dumps(da), mimetype='application/json')

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
    activity = Activity.query.filter(Activity.id == id).all()[0]
    activity.status=3
    db.session.add(activity)
    db.session.commit()
    userid=session.get('user')['userid']
    activity2 = Activity.query.filter(Activity.userid == userid).filter(Activity.status!=3).order_by(-Activity.updatetime).paginate(page, per_page,error_out=False)
    items = activity2.items
    item = []
    count = (int(page) - 1) * int(per_page)
    for i in range(len(items)):
        itemss = {'number': count + i + 1, 'id': items[i].id, 'activityname': items[i].name,
                  'type': items[i].type,'begintime': str(items[i].begintime), "endtime": str(items[i].endtime), 'status': items[i].status}
        item.append(itemss)
    data = {'zpage': activity2.pages, 'total': activity2.total, 'dpage': activity2.page, 'item': item}
    #data = sadetail(page, per_page)
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