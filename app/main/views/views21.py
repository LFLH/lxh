#video，music，image，pdf,word文件展示
from flask import request,jsonify,session,redirect,Response,make_response
from app.main import main
from app.models.models import User,Activity,AD,Data,Declare,UDeclare,Train,UTrain,Score,System,AU
from app import db
import json,datetime,random,string,os,mimetypes
from sqlalchemy import or_,and_
from werkzeug.utils import secure_filename

@main.after_app_request
def after_request(response):
    response.headers['Access-Control-Allow-Origin'] = '*'
    response.headers['Access-Control-Allow-Methods'] = 'PUT,GET,POST,DELETE'
    response.headers['Access-Control-Allow-Headers'] = 'Content-Type,Authorization'
    return response

#创建文件夹
def create_dir(s):
    file_dir = os.path.join(s)
    if not os.path.exists(file_dir):
        os.makedirs(file_dir)
    return file_dir

#word展示
@main.route('/data/word/<string:filename>', methods=['GET'])
def word(filename):
    def generate(filename):
        file_dir = create_dir('data\\word')
        path = os.path.join(file_dir, filename)
        with open(path, 'rb') as fword:
            data = fword.read(1024)
            while data:
                yield data
                data = fword.read(1024)
    return Response(generate(filename), mimetype=str(mimetypes.guess_type(filename)[0]))

#pdf展示
@main.route('/data/pdf/<string:filename>', methods=['GET'])
def pdf(filename):
    def generate(filename):
        file_dir = create_dir('data\\pdf')
        path = os.path.join(file_dir, filename)
        with open(path, 'rb') as fpdf:
            data = fpdf.read(1024)
            while data:
                yield data
                data = fpdf.read(1024)
    return Response(generate(filename), mimetype=str(mimetypes.guess_type(filename)[0]))

#图片展示
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

#音频展示
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

#视频展示
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
