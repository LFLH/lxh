#有关报告的管理
from flask import request,jsonify,session,redirect,Response,make_response
from app.main import main
from app.models.models import User,Activity,AD,Data,Declare,UDeclare,Train,UTrain,Score,System,AU,Record,DU,DUDC,TUT
from app import db
import json,datetime,random,string,os,mimetypes,time
from sqlalchemy import or_,and_
from werkzeug.utils import secure_filename

@main.after_app_request
def after_request(response):
    response.headers['Access-Control-Allow-Origin'] = '*'
    response.headers['Access-Control-Allow-Methods'] = 'PUT,GET,POST,DELETE'
    response.headers['Access-Control-Allow-Headers'] = 'Content-Type,Authorization'
    return response

#管理员条件检索
def tsmrecord(username,recordname,year,type,status,page,per_page):
    if username!=None:
        s1=(User.username.contains(username))
    else:
        s1=True
    if recordname!=None:
        s2=(Record.name.contains(recordname))
    else:
        s2=True
    if year!=None:
        s3=(Record.year==year)
    else:
        s3=True
    if type!=None:
        s4=(Record.type==type)
    else:
        s4=True
    if status is None:
        s5=True
    else:
        status=int(status)
        if status<10:
            s5=and_(User.checked==1,Record.year==datetime.datetime.now().year,Record.status==status)
        elif status<20:
            s5=and_(User.checked==1,Record.year!=datetime.datetime.now().year,Record.status==status-10)
        elif status>=20:
            s5=and_(User.checked!=1,Record.status==status-20)
    record=Record.query.join(User).filter(and_(s1,s2,s3,s4,s5)).order_by(-Record.id).paginate(page, per_page, error_out=False)
    return record

#管理员列表显示报告
@main.route('/searchrecord',methods=['GET', 'POST'])
def searchrecord():
    if request.method == "GET":
        page = request.args.get('page')#当前页
        per_page=request.args.get('per_page')#平均页数
        #检索条件
        username=request.args.get('username')#用户名
        recordname=request.args.get('recordname')#报告名称
        year=request.args.get('year')#年份
        type=request.args.get('type')#报告类型
        status=request.args.get('status')#报告状态
    else:
        page = request.form.get('page')
        per_page = request.form.get('per_page')
        # 检索条件
        username = request.form.get('username')  # 用户名
        recordname = request.form.get('recordname')  # 报告名称
        year = request.form.get('year')  # 年份
        type = request.form.get('type')  # 报告类型
        status = request.form.get('status')  # 报告状态
    page = int(page)
    per_page = int(per_page)
    #record=Record.query.order_by(-Record.id).paginate(page, per_page, error_out=False)
    record=tsmrecord(username,recordname,year,type,status,page,per_page)
    items = record.items
    item = []
    count = (int(page) - 1) * int(per_page)
    for i in range(len(items)):
        # 用户报告状态
        user = User.query.filter(User.id == items[i].userid).all()[0]
        if user.checked==1:
            if items[i].year==datetime.datetime.now().year:
                status=items[i].status#1通过0未通过
            else:
                status = 10+items[i].status  # 过去报告1通过0未通过
        else:
            status = 20 + items[i].status  # 用户考核未过报告1通过0未通过
        itemss = {'number': count + i + 1, 'id': items[i].id, 'recordname': items[i].name,'year':items[i].year,'type':items[i].type,
                  'username':user.username, 'status': status}
        item.append(itemss)
    # 返回总页数、活动总数、当前页、活动集合
    data = {'zpage': record.pages, 'total': record.total, 'dpage': record.page, 'item': item}
    return Response(json.dumps(data), mimetype='application/json')

#管理员查看报告详细信息
@main.route('/detailrecord',methods=['GET', 'POST'])
def detailrecord():
    # 根据报告id查找报告
    if request.method == "GET":
        id = request.args.get('id')
    else:
        #id = request.json.get('id')
        id = request.form.get('id')
    record =Record.query.filter(Record.id == id).all()[0]
    user=User.query.filter(User.id==record.userid).all()[0]
    data=record.datas
    filedata = {'video': [], 'image': [], 'pdf': [], 'word': []}
    for datai in data:
        dataz = {'name': datai.name, 'path': datai.path, 'newname': datai.newname}
        filedata[datai.type].append(dataz)
    # 返回报告名、报告类型、视频、图片、pdf、word
    da = {'username':user.username,'name': record.name, 'type': record.type, 'year': record.year,
          'video': filedata['video'], 'image': filedata['image'], 'pdf': filedata['pdf'],'word': filedata['word']}
    return Response(json.dumps(da), mimetype='application/json')

#通过报告
@main.route('/tgrecord',methods=['GET', 'POST'])
def tgrecord():
    # 根据报告id查找报告
    if request.method == "GET":
        id = request.args.get('id')
    else:
        #id = request.json.get('id')
        id = request.form.get('id')
    record = Record.query.filter(Record.id == id).all()[0]
    record.status = 2  # 状态，0创建，1驳回，2通过，3删除
    db.session.add(record)
    db.session.commit()
    return Response(json.dumps({'status': True}), mimetype='application/json')

#驳回报告
@main.route('/bhrecord',methods=['GET', 'POST'])
def bhrecord():
    # 根据报告id查找报告
    if request.method == "GET":
        id = request.args.get('id')
    else:
        #id = request.json.get('id')
        id = request.form.get('id')
    record = Record.query.filter(Record.id == id).all()[0]
    record.status = 1  # 状态，0创建，1驳回，2通过，3删除
    db.session.add(record)
    db.session.commit()
    return Response(json.dumps({'status': True}), mimetype='application/json')

#条件检索
def tsrecord(recordname,year,type,status,page,per_page,userid):
    if recordname!=None:
        s1=(Record.name.contains(recordname))
    else:
        s1=True
    if year!=None:
        s2=(Record.year==year)
    else:
        s2=True
    if type!=None:
        s3=(Record.type==type)
    else:
        s3=True
    if status is None:
        s4=True
    else:
        status=int(status)
        if status<10:
            s4=and_(User.checked==1,Record.year==datetime.datetime.now().year,Record.status==status)
        elif status<20:
            s4=and_(User.checked==1,Record.year!=datetime.datetime.now().year,Record.status==status-10)
        elif status>=20:
            s4=and_(User.checked!=1,Record.status==status-20)
    record=Record.query.join(User).filter(and_(s1,s2,s3,s4,User.id==userid,Record.status!=3)).order_by(-Record.id).paginate(page, per_page, error_out=False)
    return record

#user列表显示报告
@main.route('/showrecord',methods=['GET', 'POST'])
def showrecord():
    if request.method == "GET":
        page = request.args.get('page')#当前页
        per_page=request.args.get('per_page')#平均页数
        #检索条件
        recordname=request.args.get('recordname')#报告名称
        year=request.args.get('year')#年份
        type=request.args.get('type')#报告类型
        status=request.args.get('status')#报告状态
    else:
        page = request.form.get('page')
        per_page = request.form.get('per_page')
        # 检索条件
        recordname = request.form.get('recordname')  # 报告名称
        year = request.form.get('year')  # 年份
        type = request.form.get('type')  # 报告类型
        status = request.form.get('status')  # 报告状态
    page = int(page)
    per_page = int(per_page)
    user=session.get('user')
    userid=user['userid']
    #record = Record.query.filter(and_(Record.userid==userid,Record.status!=3)).order_by(-Record.id).paginate(page, per_page, error_out=False)
    record=tsrecord(recordname,year,type,status,page,per_page,userid)
    items = record.items
    item = []
    count = (int(page) - 1) * int(per_page)
    for i in range(len(items)):
        # 用户报告状态
        user = User.query.filter(User.id == items[i].userid).all()[0]
        if user.checked == 1:
            if items[i].year == datetime.datetime.now().year:
                status = items[i].status  # 1通过0未通过
            else:
                status = 10 + items[i].status  # 过去报告1通过0未通过
        else:
            status = 20 + items[i].status  # 用户考核未过报告1通过0未通过
        itemss = {'number': count + i + 1, 'id': items[i].id, 'recordname': items[i].name, 'year': items[i].year,
                  'type': items[i].type,
                  'username': user.username, 'status': status}
        item.append(itemss)
    # 返回总页数、活动总数、当前页、活动集合
    data = {'zpage': record.pages, 'total': record.total, 'dpage': record.page, 'item': item}
    return Response(json.dumps(data), mimetype='application/json')

#显示报告信息
@main.route('/detailuserrecord',methods=['GET', 'POST'])
def detailuserrecord():
    # 根据报告id查找报告
    if request.method == "GET":
        id = request.args.get('id')
    else:
        #id = request.json.get('id')
        id = request.form.get('id')
    record = Record.query.filter(Record.id == id).all()[0]
    user=User.query.filter(User.id==record.userid).all()[0]
    data = record.datas
    filedata = {'video': [], 'image': [], 'pdf': [], 'word': []}
    for datai in data:
        dataz = {'name': datai.name, 'path': datai.path, 'newname': datai.newname}
        filedata[datai.type].append(dataz)
    # 返回报告名、报告类型、视频、图片、pdf、word
    da = {'username':user.username,'name': record.name, 'type': record.type, 'year': record.year,
          'video': filedata['video'], 'image': filedata['image'], 'pdf': filedata['pdf'], 'word': filedata['word']}
    return Response(json.dumps(da), mimetype='application/json')

#删除报告
@main.route('/deleterecord',methods=['GET', 'POST'])
def deleterecord():
    # 根据报告id查找报告
    if request.method == "GET":
        id = request.args.get('id')
    else:
        #id = request.json.get('id')
        id = request.form.get('id')
    record = Record.query.filter(Record.id == id).all()[0]
    record.status = 3  # 状态，0创建，1驳回，2通过，3删除
    db.session.add(record)
    db.session.commit()
    return Response(json.dumps({'status': True}), mimetype='application/json')

#判断上传文件类型
def panduan(ext):
    video = ['asf', 'asx', 'dvr-ms', 'wm', 'wmp', 'wmv', 'ra', 'ram', 'rm', 'rmvb', 'mov', 'qt', 'f4v', 'flv', 'hlv',
             'swf', 'ifo', 'vob', 'dat', 'm1v', 'm2p', 'm2t', 'm2ts', 'm2v', 'm4b', 'm4p', 'm4v', 'mp2v', 'mp4', 'mpe',
             'mpeg', 'mpeg4', 'mpg', 'mpv2', 'pva', 'tp', 'ts', 'mpeg1', 'mpeg2', '3g2', '3gp', '3gp2', '3gpp', '2634',
             'amv', 'avi', 'bik', 'divx', 'dpg', 'evo', 'h264', 'ivm', 'k3g', 'mkv', 'mod', 'mp4v', 'mts', 'nsr', 'nsv',
             'ogm', 'ogv', 'pfv', 'pmf', 'pmp', 'pss', 'scm', 'skm', 'tod', 'tpr', 'trp', 'vp6', 'vp7', 'webm', 'wtv',
             'mp41', 'dv', 'mtv', 'mxf', 'vro', 'vdat']
    image=['bmp','pcx','png','gif','jpeg','tiff','cgm','dxf','cdr','wmf','eps','emf','pict','jpg']
    word=['doc','docx']
    pdf=['pdf']
    if ext in video:
        type = 'video'
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

#创建文件夹树
def createdirtree(userid):
    # 创建文件夹树
    file_dir ={}
    # 创建基本文件夹data
    file_dir['base']=create_dir('data')
    # 创建输出文件夹data/userout
    file_dir['userout'] = create_dir('data/userout')
    # 创建用户文件夹
    user=User.query.filter(User.id==userid).all()[0]
    file_dir['user'] = create_dir('data/userout/' + user.name)
    #创建活动文件夹
    activity=Activity.query.filter(Activity.userid==userid).all()
    file_dir['activity'] ={}
    abase=create_dir('data/userout/'+user.name+'/自主活动')#video,music,image,pdf,word
    activitytype=['video','music','image','pdf','word']
    file_dir['activity']['base']=abase
    for a in activity:
        ai={}
        ai['base']=create_dir('data/userout/'+user.name+'/自主活动/'+a.name)
        for type in activitytype:
            ai[type]=create_dir('data/userout/'+user.name+'/自主活动/'+a.name+'/'+type)
        file_dir['activity'][str(a.id)]=ai
    # 创建申报文件夹
    file_dir['declare'] = {}
    dbase = create_dir('data/userout/' + user.name + '/申报')#pdf,word
    file_dir['declare']['base']=dbase
    declaretype = ['pdf', 'word']
    #创建用户相关申报文件夹
    declare=Declare.query.join(DU).join(User).filter(User.id==userid).all()
    for d in declare:
        di={}
        di['base']=create_dir('data/userout/' + user.name + '/申报/'+d.name)
        udeclare=UDeclare.query.join(DUDC).join(Declare).filter(Declare.id==d.id).all()
        for ud in udeclare:
            udi={}
            udi['base']=create_dir('data/userout/' + user.name + '/申报/'+d.name+'/'+str(ud.id))
            for type in declaretype:
                udi[type]=create_dir('data/userout/' + user.name + '/申报/'+d.name+'/'+str(ud.id)+'/'+type)
            di[str(ud.id)]=udi
        file_dir['declare'][d.name]=di
    # 创建培训文件夹
    file_dir['train'] = {}
    tbase = create_dir('data/userout/' + user.name + '/培训')#image,pdf,word
    file_dir['train']['base']=tbase
    traintype=['image','pdf','word']
    #创建用户相关培训文件夹
    train=Train.query.join(TUT).join(UTrain).filter(UTrain.userid==userid).all()
    for t in train:
        ti={}
        ti['base']=('data/userout/' + user.name + '/培训/'+t.name)
        utrain=UTrain.query.join(TUT).join(Train).filter(Train.id==t.id).all()
        for ut in utrain:
            uti={}
            uti['base']=create_dir('data/userout/' + user.name + '/培训/'+t.name+'/'+str(ut.id))
            for type in traintype:
                uti[type]=create_dir('data/userout/' + user.name + '/培训/'+t.name+'/'+str(ut.id)+'/'+type)
            ti[str(ut.id)]=uti
        file_dir['train'][t.name]=ti
    # 创建年度报告文件夹
    record1 = Record.query.filter(and_(Record.userid == userid, Record.type == '年度')).all()
    file_dir['ndreport'] = {}
    ndrbase = create_dir('data/userout/' + user.name + '/年度报告')#mage,pdf,word
    ndtype=['image','pdf','word']
    file_dir['ndreport']['base']=ndrbase
    for nr in record1:
        ndri={}
        ndri['base'] = create_dir('data/userout/' + user.name + '/年度报告/' + nr.name)
        for type in ndtype:
            ndri[type]=create_dir('data/userout/' + user.name + '/年度报告/' + nr.name+'/'+type)
        file_dir['ndreport'][str(nr.id)]=ndri
    # 创建科技周报告文件夹
    record2 = Record.query.filter(and_(Record.userid == userid, Record.type == '科技周')).all()
    file_dir['kjzreport'] = {}
    kjzrbase = create_dir('data/userout/' + user.name + '/科技周报告')#video,image,pdf,word
    kjztype=['video','image','pdf','word']
    file_dir['kjzreport']['base']=kjzrbase
    for kjr in record2:
        kjzri={}
        kjzri['base'] = create_dir('data/userout/' + user.name + '/科技周报告/' + kjr.name)
        for type in kjztype:
            kjzri[type]=create_dir('data/userout/' + user.name + '/科技周报告/' + kjr.name+'/'+type)
        file_dir['kjzreport'][str(kjr.id)]=kjzri
    # 创建zip文件夹
    file_dir['zip'] = create_dir('data/zip')
    return file_dir

#修改报告
@main.route('/updaterecord',methods=['GET', 'POST'])
def updaterecord():
    # 检查文件类型及尺寸
    files = request.files.getlist('files')
    filedata = []
    for file in files:
        filename = secure_filename(file.filename)
        ext = filename.rsplit('.')
        ext = ext[len(ext) - 1].lower()
        type = panduan(ext)
        filedata.append(file.read())
        j = len(filedata) - 1
        size = int(len(filedata[j]) / 1024 / 1024)
        if type == 'error' or size > 100:
            return Response(json.dumps({'status': False, 'code': 500}), mimetype='application/json')
    id = request.args.get('id')
    name = request.args.get('name')
    data = request.args.get('data')
    data = data.split(',')
    data[0] = data[0].split('[')[1]
    data[len(data) - 1] = data[len(data) - 1].split(']')[0]
    for i in range(len(data)):
        if data[i] != '':
            data[i] = int(data[i])
    user = session.get('user')
    userid = user['userid']
    user = User.query.filter(User.id == userid).all()[0]
    # 根据报告id查找报告
    record = Record.query.filter(Record.id == id).all()[0]
    # 修改报告信息
    if name!=None:
        record.name = name
    datas = record.datas
    # 移除活动中的文件
    length = len(datas)
    for i in range(length):
        record.datas.remove(datas[length - i - 1])
    #修改文件列表
    for did in data:
        if did!='':
            diddata=Data.query.filter(Data.id==did).all()[0]
            record.datas.append(diddata)
    db.session.add(record)
    db.session.commit()
    # 修改用户操作时间
    user.updatetime = datetime.datetime.now()
    db.session.add(user)
    db.session.commit()
    # 创建文件夹树
    file_dir = createdirtree(userid)
    # 保存文件
    for i in range(len(files)):
        file = files[i]
        filename = secure_filename(file.filename)
        ext = filename.rsplit('.')
        ext = ext[len(ext) - 1].lower()  # 获取文件后缀
        type = panduan(ext)
        timestamp = str(time.mktime(time.strptime(str(user.updatetime), "%Y-%m-%d %H:%M:%S")))
        new_filename = str(user.username) + "_" + str(record.name) + "_" + timestamp + "_" + str(i + 1) + '.' + ext  # 修改了上传的文件名
        if record.type=='科技周':
            status='kjzreport'
        else:
            status='ndreport'
        path=file_dir[str(status)][str(record.id)][str(type)]  # 保存文件的目录
        file.save(os.path.join(path, new_filename))  # 保存文件到目录
        file_data = path + '/' + new_filename
        f = open(file_data, 'wb')
        f.write(filedata[i])
        f.close()
        data = Data(name=file.filename, type=type, path=file_data, newname=new_filename)
        db.session.add(data)
        db.session.commit()
        record.datas.append(data)
    db.session.add(record)
    db.session.commit()
    return Response(json.dumps({'status': True, 'code': 200}), mimetype='application/json')
