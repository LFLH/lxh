#/userupdata的后端API
from flask import request,jsonify,session,redirect,Response
from app.main import main
from app.models.models import User,Activity,AD,Data,Declare,UDeclare,Train,UTrain,Score,System,DU,TUT,DUDC,Record
from app import db
import json,datetime,random,string,os,time
from sqlalchemy import or_,and_
from werkzeug.utils import secure_filename

@main.after_app_request
def after_request(response):
    response.headers['Access-Control-Allow-Origin'] = '*'
    response.headers['Access-Control-Allow-Methods'] = 'PUT,GET,POST,DELETE'
    response.headers['Access-Control-Allow-Headers'] = 'Content-Type,Authorization'
    return response

#判断文件类型
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

#自主活动提交
@main.route('/addactivitycs',methods=['GET','POST'])
def addactivitycs():
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
    # 创建用户自主活动
    user = session.get('user')
    userid = user['userid']
    user = User.query.filter(User.id == userid).all()[0]
    name = request.args.get('name')
    begintime = request.args.get('begintime')
    endtime = request.args.get('endtime')
    main = request.args.get('main')
    type = request.args.get('type')
    begintime = datetime.datetime.strptime(begintime, '%Y-%m-%dT%H:%M')
    endtime = datetime.datetime.strptime(endtime, '%Y-%m-%dT%H:%M')
    activity = Activity(name=name, typeuser='自主', begintime=begintime, endtime=endtime, main=main, type=type,userid=userid)
    db.session.add(activity)
    db.session.commit()
    # 修改用户操作时间
    user.updatetime = activity.updatetime
    db.session.add(user)
    db.session.commit()
    # 创建文件夹树
    file_dir = createdirtree(userid)
    # 保存文件
    for i in range(len(files)):
        file=files[i]
        filename = secure_filename(file.filename)
        ext = filename.rsplit('.')
        ext = ext[len(ext) - 1].lower()  # 获取文件后缀
        type = panduan(ext)
        timestamp = str(time.mktime(time.strptime(str(activity.updatetime), "%Y-%m-%d %H:%M:%S")))
        new_filename = str(user.username) + "_" + str(activity.name) + "_" + timestamp + "_" + str(i + 1) + '.' + ext  # 修改了上传的文件名
        path = file_dir['activity'][str(activity.id)][str(type)]  # 保存文件的目录
        file.save(os.path.join(path, new_filename))  # 保存文件到目录
        file_data = path + '/' + new_filename
        f = open(file_data, 'wb')
        f.write(filedata[i])
        f.close()
        data = Data(name=file.filename, type=type, path=file_data, newname=new_filename)
        db.session.add(data)
        db.session.commit()
        activity.datas.append(data)
    db.session.add(activity)
    db.session.commit()
    return Response(json.dumps({'status': True}), mimetype='application/json')
