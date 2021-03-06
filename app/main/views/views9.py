#/manageuser的后端API
from flask import request,jsonify,session,redirect,Response,send_file
from app.main import main
from app.models.models import User,Activity,AD,Data,Declare,UDeclare,Train,UTrain,Score,Record,DUDC,TUT,DU
from app import db
import json,datetime,random,string,os,xlrd,xlwt,time,mimetypes,zipfile
from sqlalchemy import or_,and_
from werkzeug.utils import secure_filename
from shutil import copyfile

@main.after_app_request
def after_request(response):
    response.headers['Access-Control-Allow-Origin'] = '*'
    response.headers['Access-Control-Allow-Methods'] = 'PUT,GET,POST,DELETE'
    response.headers['Access-Control-Allow-Headers'] = 'Content-Type,Authorization'
    return response

#添加用户
@main.route('/adduser',methods=['GET', 'POST'])
def adduser():
    #根据用户名添加用户
    if request.method == "GET":
        name = request.args.get('name')
        email =request.args.get('email')
        phone=request.args.get('phone')
        address=request.args.get('address')
    else:
        name = request.form.get('name')
        email = request.form.get('email')
        phone = request.form.get('phone')
        address = request.form.get('address')
    user=User.query.filter(User.name==name).all()
    #不存在用户
    if len(user)==0:
        k = random.randint(6, 8)
        #生成用户名
        year=str(datetime.datetime.now().year)
        month=int(datetime.datetime.now().month)
        if month<10:
            month='0'+str(month)
        else:
            month=str(month)
        s=year+month+'%'
        bh=User.query.filter(User.username.like(s)).count()+1
        if bh<10:
            bh='00'+str(bh)
        elif bh<100:
            bh='0'+str(bh)
        else:
            bh=str(bh)
        username=year+month+bh
        #自动生成密码
        password=''.join(random.sample(string.ascii_letters + string.digits, k))
        #添加用户
        newuser=User(username=username,name=name,email=email,phone=phone,address=address,password=password,type='user',checked=0)
        db.session.add(newuser)
        db.session.commit()
    #存在用户
    else:
        user[0].checked=0
        user[0].endtime=datetime.datetime.now()
        db.session.add(user[0])
        db.session.commit()
    return Response(json.dumps({'status': True}), mimetype='application/json')

#批量导入
@main.route('/exceladduser',methods=['GET', 'POST'])
def exceladduser():
    # 创建存储地址data文件夹
    file_dir = os.path.join('data')
    if not os.path.exists(file_dir):
        os.makedirs(file_dir)
    # 创建存储地址data\sysactivity文件夹
    file_dir = os.path.join('data\\user')
    if not os.path.exists(file_dir):
        os.makedirs(file_dir)
    # 创建Excel存储
    upload_files=request.files.getlist('excel')
    for file in upload_files:
        filename = secure_filename(file.filename)
        ext = filename.rsplit('.')
        ext = ext[len(ext) - 1].lower()  # 获取文件后缀
        new_filename = "user" + '.' + ext  # 修改了上传的文件名
        file.save(os.path.join(file_dir, new_filename))  # 保存文件到目录
        file_data = 'data\\user\\'+ new_filename
        # 打开文件
        workBook = xlrd.open_workbook(file_data)
        #按索引号获取sheet内容
        sheet1_content1 = workBook.sheet_by_index(0)  # sheet索引从0开始
        nrows=sheet1_content1.nrows
        for i in range(nrows):
            if i!=0:
                name=sheet1_content1.cell(i, 1).value#科普单位
                email =sheet1_content1.cell(i, 2).value#邮箱
                phone =sheet1_content1.cell(i, 3).value#联系电话
                address =sheet1_content1.cell(i, 4).value#地址
                user = User.query.filter(User.name == name).all()
                # 不存在用户
                if len(user) == 0:
                    k = random.randint(6, 8)
                    # 生成用户名
                    year = str(datetime.datetime.now().year)
                    month = int(datetime.datetime.now().month)
                    if month < 10:
                        month = '0' + str(month)
                    else:
                        month = str(month)
                    s = year + month + '%'
                    bh = User.query.filter(User.username.like(s)).count() + 1
                    if bh < 10:
                        bh = '00' + str(bh)
                    elif bh < 100:
                        bh = '0' + str(bh)
                    else:
                        bh = str(bh)
                    username = year + month + bh
                    # 自动生成密码
                    password = ''.join(random.sample(string.ascii_letters + string.digits, k))
                    # 添加用户
                    newuser = User(username=username, name=name, email=email, phone=phone, address=address,password=password, type='user', checked=1)
                    db.session.add(newuser)
                    db.session.commit()
    return Response(json.dumps({'status': True}), mimetype='application/json')

#查看用户信息
@main.route('/detailuser',methods=['GET', 'POST'])
def detailuser():
    if request.method == "GET":
        id = request.args.get('id')
    else:
        id = request.form.get('id')
    user=User.query.filter(User.id==id).all()[0]
    if user.checked == 0:
        if user.endtime > datetime.datetime.now():
            status = 0  # 新用户
        else:
            status = 1  # 未激活用户
    elif user.checked == 1:
        status = 2  # 正式用户
    else:
        status = 3  # 考核未过用户
    users={'username':user.username,'name':user.name,'email':user.email,'phone':user.phone,'address':user.address,'password':user.password,'type':user.type,'status':status}
    return Response(json.dumps(users), mimetype='application/json')

#条件检索
def tsuser(username,status,page,per_page):
    if username!=None:
        s1=(User.username.contains(username))
    else:
        s1=True
    if status!=None:
        status=int(status)
        if status==0:
            s2=and_(User.checked==0,User.endtime>datetime.datetime.now())
        elif status==1:
            s2=and_(User.checked==0,User.endtime<datetime.datetime.now())
        elif status==2:
            s2=(User.checked==1)
        elif status==3:
            s2=(User.checked==2)
    else:
        s2=True
    user=User.query.filter(and_(User.type != 'sysadmin',s1,s2)).order_by(-User.updatetime).paginate(page, per_page, error_out=False)
    return user

#删除用户
@main.route('/deleteuser',methods=['GET', 'POST'])
def deleteuser():
    if request.method == "GET":
        id = request.args.get('id')
        page = request.args.get('page')  # 当前页
        per_page = request.args.get('per_page')  # 平均页数
        # 检索条件
        username = request.args.get('username')  # 用户名
        status = request.args.get('status')  # 用户类型
    else:
        id = request.form.get('id')
        page = request.form.get('page')
        per_page = request.form.get('per_page')
        # 检索条件
        username = request.form.get('username')  # 用户名
        status = request.form.get('status')  # 用户类型
    #移除用户的相关活动及数据
    page = int(page)
    per_page = int(per_page)
    user=User.query.filter(User.id==id).all()[0]
    user.checked=2#删除标识
    # 倒叙：在排序的时候使用这个字段的字符串名字，然后在前面加一个负号
    user = tsuser(username,status,page,per_page)
    items = user.items
    item = []
    count = (int(page) - 1) * int(per_page)
    for i in range(len(items)):
        if items[i].checked==0:
            if items[i].endtime>datetime.datetime.now():
                status=0#新用户
            else:
                status=1#未激活用户
        elif items[i].checked==1:
            status=2#正式用户
        else:
            status=3#考核未过用户
        # 返回用户id，用户名，密码，最后操作时间，状态
        itemss = {'number': count + i + 1, 'id': items[i].id, 'username': items[i].username,
                  'password': items[i].password, 'lasttime': str(items[i].updatetime), 'status': status}
        item.append(itemss)
    # 返回总页数、活动总数、当前页、用户集合
    data = {'zpage': user.pages, 'total': user.total, 'dpage': user.page, 'item': item}
    return Response(json.dumps(data), mimetype='application/json')

#列表显示用户
@main.route('/searchuser',methods=['GET', 'POST'])
def searchuser():
    if request.method == "GET":
        page = request.args.get('page')#当前页
        per_page=request.args.get('per_page')#平均页数
        #检索条件
        username=request.args.get('username')#用户名
        status=request.args.get('status')#用户类型
    else:
        page = request.form.get('page')
        per_page = request.form.get('per_page')
        # 检索条件
        username = request.form.get('username')#用户名
        status = request.form.get('status')#用户类型
    #倒叙：在排序的时候使用这个字段的字符串名字，然后在前面加一个负号
    page=int(page)
    per_page = int(per_page)
    #查询用户需要sysadmin用户和老用户、未过期用户
    user=tsuser(username,status,page,per_page)
    #user=User.query.filter(User.type != 'sysadmin').order_by(-User.updatetime).paginate(page, per_page, error_out=False)
    items=user.items
    item=[]
    count=(int(page)-1)*int(per_page)
    for i in range(len(items)):
        if items[i].checked==0:
            if items[i].endtime>datetime.datetime.now():
                status=0#新用户
            else:
                status=1#未激活用户
        elif items[i].checked==1:
            status=2#正式用户
        else:
            status=3#考核未过用户
        #返回用户id，用户名，密码，最后操作时间，状态
        itemss={'number':count+i+1,'id':items[i].id,'username':items[i].username,'name':items[i].name,'password':items[i].password,'lasttime':str(items[i].updatetime),'status':status}
        item.append(itemss)
    # 返回总页数、活动总数、当前页、用户集合
    data={'zpage':user.pages,'total':user.total,'dpage':user.page,'item':item}
    return Response(json.dumps(data), mimetype='application/json')

#用户导出
@main.route('/userout',methods=['GET', 'POST'])
def userout():
    userz=User.query.filter(and_(User.checked==0,User.endtime>datetime.datetime.now(),User.type=='user')).all()
    user = []
    for users in userz:
        u={'username':users.username,'name':users.name,'password':users.password,'email':users.email,'phone':users.phone,'address':users.address}
        user.append(u)
        # 创建存储地址data文件夹
    file_dir = os.path.join('data')
    if not os.path.exists(file_dir):
        os.makedirs(file_dir)
    # 创建存储地址data\sysactivity文件夹
    file_dir = os.path.join('data\\user')
    if not os.path.exists(file_dir):
        os.makedirs(file_dir)
    # 创建以时间戳为Excel表存储地址名
    timestamp = str(time.mktime(datetime.datetime.now().timetuple()))
    file_new_dir = os.path.join('data\\user\\' + timestamp)
    if not os.path.exists(file_new_dir):
        os.makedirs(file_new_dir)
        # 创建Excel表
    excelTabel = xlwt.Workbook()  # 创建excel对象
    endtime = str(userz[0].endtime).split('-')
    endtime = endtime[0] + '年' + endtime[1] + '月' + endtime[2].split(' ')[0] + '日'
    name = str(endtime + "截止申报新用户表")
    sheet1 = excelTabel.add_sheet(name, cell_overwrite_ok=True)
    # 填写内容
    alignment = xlwt.Alignment()  # Create Alignment  创建对齐
    alignment.horz = xlwt.Alignment.HORZ_CENTER  # May be: 标准化：HORZ_GENERAL, 左对齐：HORZ_LEFT, 水平对齐居中：HORZ_CENTER, 右对齐：HORZ_RIGHT, 填充：HORZ_FILLED, HORZ_JUSTIFIED, HORZ_CENTER_ACROSS_SEL, HORZ_DISTRIBUTED
    alignment.vert = xlwt.Alignment.VERT_CENTER  # May be: 顶部对齐：VERT_TOP, 垂直居中：VERT_CENTER, 底部对齐：VERT_BOTTOM, VERT_JUSTIFIED, VERT_DISTRIBUTED
    style = xlwt.XFStyle()  # Create Style 创建样式
    style.alignment = alignment  # Add Alignment to Style  为样式添加对齐
    sheet1.write_merge(0, 0, 0, 6, name,style)
    sheet1.write(1, 0, "新用户单位编号")
    sheet1.write(1, 1, "用户的实际单位名")
    sheet1.write(1, 2, "系统登录用户名")
    sheet1.write(1, 3, "系统登录用户密码")
    sheet1.write(1, 4, "用户邮箱")
    sheet1.write(1, 5, "用户联系电话")
    sheet1.write(1, 6, "用户地址")
    for i in range(len(user)):
        sheet1.write(i + 2, 0, i+1)
        sheet1.write(i+2, 1, str(user[i]['name']))
        sheet1.write(i + 2, 2, str(user[i]['username']))
        sheet1.write(i + 2, 3, str(user[i]['password']))
        sheet1.write(i + 2, 4, str(user[i]['email']))
        sheet1.write(i + 2, 5, str(user[i]['phone']))
        sheet1.write(i + 2, 6, str(user[i]['address']))
    # 以时间戳为Excel文件名
    excelTabel.save('data\\user\\' + timestamp+ '\\' + name + '.xlsx')
    # 获取文件名及文件绝对路径并将文件上传给前端
    filename = name + '.xlsx'
    file1 = str(os.path.abspath(__file__))
    filed = file1.split('app')[0]
    directory = filed +'data\\user\\' + timestamp+ '\\'
    return send_file(directory + filename, mimetype=str(mimetypes.guess_type(filename)[0]),attachment_filename=filename.encode('utf-8').decode('latin1'), as_attachment=True)

#重置密码
@main.route('/setpassword',methods=['GET', 'POST'])
def setpassword():
    #根据用户名添加用户
    if request.method == "GET":
        id = request.args.get('id')
        page = request.args.get('page')  # 当前页
        per_page = request.args.get('per_page')  # 平均页数
        # 检索条件
        username = request.args.get('username')  # 用户名
        status = request.args.get('status')  # 用户类型
    else:
        id = request.form.get('id')
        page = request.form.get('page')
        per_page = request.form.get('per_page')
        # 检索条件
        username = request.form.get('username')  # 用户名
        status = request.form.get('status')  # 用户类型
    page=int(page)
    per_page=int(per_page)
    user=User.query.filter(User.id==id).all()[0]
    k = random.randint(6, 8)
    # 自动生成密码
    password = ''.join(random.sample(string.ascii_letters + string.digits, k))
    user.password=password
    db.session.add(user)
    db.session.commit()
    # 倒叙：在排序的时候使用这个字段的字符串名字，然后在前面加一个负号
    user = tsuser(username,status,page,per_page)
    items = user.items
    item = []
    count = (int(page) - 1) * int(per_page)
    for i in range(len(items)):
        if items[i].checked == 0:
            if items[i].endtime > datetime.datetime.now():
                status = 0  # 新用户
            else:
                status = 1  # 未激活用户
        elif items[i].checked == 1:
            status = 2  # 正式用户
        else:
            status = 3  # 考核未过用户
        # 返回用户id，用户名，密码，最后操作时间，状态
        itemss = {'number': count + i + 1, 'id': items[i].id, 'username': items[i].username,
                  'password': items[i].password, 'lasttime': str(items[i].updatetime), 'status': status}
        item.append(itemss)
    # 返回总页数、活动总数、当前页、用户集合
    data = {'zpage': user.pages, 'total': user.total, 'dpage': user.page, 'item': item}
    return Response(json.dumps(data), mimetype='application/json')

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

#批量用户文档导出
@main.route('/useroutdata',methods=['GET', 'POST'])
def useroutdata():
    if request.method == "GET":
        id = request.args.get('id')
    else:
        id = request.form.get('id')
    # 创建文件夹树
    file_dir = createdirtree(id)
    user=User.query.filter(User.id==id).all()[0]
    #压缩文件
    startdir = file_dir['user']  # 要压缩的文件夹路径
    file_news = file_dir['zip']+'/'+str(user.name)+'.zip'  # 压缩后文件夹的名字
    z = zipfile.ZipFile(file_news, 'w', zipfile.ZIP_DEFLATED)  # 参数一：文件夹名
    for dirpath, dirnames, filenames in os.walk(startdir):
        fpath = dirpath.replace(startdir, '')  # 这一句很重要，不replace的话，就从根目录开始复制
        fpath = fpath and fpath + os.sep or ''  # 这句话理解我也点郁闷，实现当前文件夹以及包含的所有文件的压缩
        for filename in filenames:
            z.write(os.path.join(dirpath, filename), fpath + filename)
    z.close()
    filename=str(user.name)+'.zip'
    file1 = str(os.path.abspath(__file__))
    filed = file1.split('app')[0]
    directory = filed +file_dir['zip']+ '\\'
    return send_file(directory + filename, mimetype=str(mimetypes.guess_type(filename)[0]),attachment_filename=filename.encode('utf-8').decode('latin1'), as_attachment=True)