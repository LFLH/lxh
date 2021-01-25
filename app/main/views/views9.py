#/manageuser的后端API
from flask import request,jsonify,session,redirect,Response
from app.main import main
from app.models.models import User,Activity,AD,Data,Declare,UDeclare,Train,UTrain,Score
from app import db
import json,datetime,random,string,os,xlrd,xlwt
from sqlalchemy import or_,and_
from werkzeug.utils import secure_filename

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
        username = request.args.get('username')
    else:
        username = request.json.get('username')
    user=User.query.filter(User.username==username).all()
    maxdate='9999-12-31 23:59:59'
    maxdate=datetime.datetime.strptime(maxdate, '%Y-%m-%d %H:%M:%S')
    #不存在用户
    if len(user)==0:
        k = random.randint(8, 20)
        #自动生成密码
        password=''.join(random.sample(string.ascii_letters + string.digits, k))
        #添加用户
        newuser=User(username=username,password=password,type='user',checked=0,endtime=maxdate)
        db.session.add(newuser)
        db.session.commit()
    #存在用户
    else:
        user[0].checked=0
        user[0].endtime=maxdate
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
                username=sheet1_content1.cell(i, 0).value#用户名
                name=sheet1_content1.cell(i, 1).value#科普单位
                email =sheet1_content1.cell(i, 2).value#邮箱
                phone =sheet1_content1.cell(i, 3).value#联系电话
                address =sheet1_content1.cell(i, 4).value#地址
                user = User.query.filter(User.username == username).all()
                # 不存在用户
                if len(user) == 0:
                    k = random.randint(8, 20)
                    # 自动生成密码
                    password = ''.join(random.sample(string.ascii_letters + string.digits, k))
                    # 添加用户
                    newuser = User(username=username, password=password, type='user', checked=1,name=name,email=email,phone=phone,address=address)
                    db.session.add(newuser)
                    db.session.commit()
    return Response(json.dumps({'status': True}), mimetype='application/json')

#删除用户
@main.route('/deleteuser',methods=['GET', 'POST'])
def deleteuser():
    if request.method == "GET":
        id = request.args.get('id')
        page = request.args.get('page')  # 当前页
        per_page = request.args.get('per_page')  # 平均页数
    else:
        id = request.json.get('id')
        page = request.json.get('page')
        per_page = request.json.get('per_page')
    #移除用户的相关活动及数据
    page = int(page)
    per_page = int(per_page)
    user=User.query.filter(User.id==id).all()[0]
    user.checked=2#删除标识
    # 倒叙：在排序的时候使用这个字段的字符串名字，然后在前面加一个负号
    user = User.query.filter(User.type != 'sysadmin').order_by(-User.updatetime).paginate(page, per_page, error_out=False)
    items = user.items
    item = []
    count = (int(page) - 1) * int(per_page)
    for i in range(len(items)):
        if user.checked==0:
            if user.endtime>datetime.datetime.now():
                status=0#新用户
            else:
                status=1#未激活用户
        elif user.checked==1:
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
    else:
        page = request.json.get('page')
        per_page = request.json.get('per_page')
    #倒叙：在排序的时候使用这个字段的字符串名字，然后在前面加一个负号
    page=int(page)
    per_page = int(per_page)
    #查询用户需要sysadmin用户和老用户、未过期用户
    user=User.query.filter(User.type != 'sysadmin').order_by(-User.updatetime).paginate(page, per_page, error_out=False)
    items=user.items
    item=[]
    count=(int(page)-1)*int(per_page)
    for i in range(len(items)):
        if user.checked==0:
            if user.endtime>datetime.datetime.now():
                status=0#新用户
            else:
                status=1#未激活用户
        elif user.checked==1:
            status=2#正式用户
        else:
            status=3#考核未过用户
        #返回用户id，用户名，密码，最后操作时间，状态
        itemss={'number':count+i+1,'id':items[i].id,'username':items[i].username,'password':items[i].password,'lasttime':str(items[i].updatetime),'status':status}
        item.append(itemss)
    # 返回总页数、活动总数、当前页、用户集合
    data={'zpage':user.pages,'total':user.total,'dpage':user.page,'item':item}
    return Response(json.dumps(data), mimetype='application/json')

