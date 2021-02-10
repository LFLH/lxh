#video，music，image，pdf,word文件导出
from flask import request,jsonify,session,redirect,Response,make_response,send_file,render_template
from app.main import main
from app.models.models import User,Activity,AD,Data,Declare,UDeclare,Train,UTrain,Score,System,AU,Record
from app import db
import json,datetime,random,string,os,mimetypes
from sqlalchemy import or_,and_
from werkzeug.utils import secure_filename
import urllib.parse

#单独文件导出
@main.route('/download/data/<path:path>',methods=['GET', 'POST'])
def download_data(path):
    path=urllib.parse.unquote(path)
    file1 = str(os.path.abspath(__file__))
    filed = file1.split('app')[0]
    directory_filename=filed+'data/'+path
    s=str(directory_filename).split('/')
    filename=s[len(s)-1]
    return send_file(directory_filename, mimetype=str(mimetypes.guess_type(filename)[0]),attachment_filename=filename.encode('utf-8').decode('latin1'), as_attachment=True)

#申报文件批量导出
@main.route('/download/declare/<int:id>',methods=['GET', 'POST'])
def download_declare(id):
    udeclare=UDeclare.query.filter(UDeclare.id==id).all()[0]
    datas=udeclare.datas
    url=[]
    for data in datas:
        url.append('/download/'+data.path)
    return Response(json.dumps({'url':url}), mimetype='application/json')

#培训文件批量导出
@main.route('/download/train/<int:id>',methods=['GET', 'POST'])
def download_train(id):
    utrain=UTrain.query.filter(UTrain.id==id).all()[0]
    datas=utrain.datas
    url=[]
    for data in datas:
        url.append('/download/'+data.path)
    return Response(json.dumps({'url':url}), mimetype='application/json')

#自主活动文件批量导出
@main.route('/download/zhactivity/<int:id>',methods=['GET', 'POST'])
def download_zhactivity(id):
    activity=Activity.query.filter(Activity.id==id).all()[0]
    datas=activity.datas
    url=[]
    for data in datas:
        url.append('/download/'+data.path)
    return Response(json.dumps({'url':url}), mimetype='application/json')

#报告文件批量导出
@main.route('/download/record/<int:id>',methods=['GET', 'POST'])
def download_record(id):
    record=Record.query.filter(Record.id==id).all()[0]
    datas=record.datas
    url=[]
    for data in datas:
        url.append('/download/'+data.path)
    return Response(json.dumps({'url':url}), mimetype='application/json')

#用户所有文件批量导出
@main.route('/download/user/<int:id>',methods=['GET', 'POST'])
def download_user(id):
    url = []
    #申报文件
    udeclare=UDeclare.query.filter(UDeclare.userid==id).all()
    for ud in udeclare:
        datas=ud.datas
        for data in datas:
            url.append('/download/'+data.path)
    #培训文件
    utrain=UTrain.query.filter(UTrain.userid==id).all()
    for ut in utrain:
        datas=ut.datas
        for data in datas:
            url.append('/download/' + data.path)
    #自主活动文件
    activitys=Activity.query.filter(Activity.userid==id).all()
    for activity in activitys:
        datas=activity.datas
        for data in datas:
            url.append('/download/' + data.path)
    #报告文件
    records=Record.query.filter(Record.userid==id).all()
    for record in records:
        datas=record.datas
        for data in datas:
            url.append('/download/' + data.path)
    return Response(json.dumps({'url':url}), mimetype='application/json')

#下载测试
@main.route('/cs7',methods=['GET', 'POST'])
def cs7():
    return render_template('cs7.html')