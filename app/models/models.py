from app import db
import datetime

#表 1用户表
class User(db.Model):
    __tablename__ = 'user'
    id=db.Column(db.Integer, primary_key=True,autoincrement=True )#用户id
    username=db.Column(db.String(255))#用户名，科普基地单位名称
    password=db.Column(db.String(255))#密码，口令
    type = db.Column(db.String(255))  # sysadmin或user
    checked=db.Column(db.Integer)#单位类别,0或1
    updatetime = db.Column(db.DateTime, default=datetime.datetime.now)  # 最后操作更新时间
    endtime = db.Column(db.DateTime, default=datetime.datetime.now)  # 申报截止时间
    usersa = db.relationship('Activity', backref='usera')#Activity外键
    userudc=db.relationship('UDeclare', backref='userudc')#UDeclare外键
    userut = db.relationship('UTrain', backref='userut')  # UTrain外键
    usersr = db.relationship('Record', backref='userr')  # Record外键
    usersc=db.relationship('Score',backref='usersc')# Score外键
    uersau=db.relationship('AU', backref='userau')#AU外键

    def __repr__(self):
        return self

#表 4活动文件表(活动id,文件id)
AD = db.Table('ad', db.Column('activityid', db.Integer, db.ForeignKey('activity.id')),db.Column('dataid', db.Integer, db.ForeignKey('data.id')))

#表 5活动报名表(活动id,用户id，状态,ip地址)
class AU(db.Model):
    __tablename__='au'
    activityid=db.Column(db.Integer, db.ForeignKey('activity.id'),primary_key=True)
    userid=db.Column(db.Integer, db.ForeignKey('user.id'),primary_key=True)
    type=db.Column(db.Integer,default=0)
    ip=db.Column(db.String(255))

    def __repr__(self):
        return self

#表 2活动表
class Activity(db.Model):
    __tablename__='activity'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)  # 活动id
    name=db.Column(db.String(255))    #活动名
    typeuser=db.Column(db.String(255))    #活动类别，自主或系统
    type=db.Column(db.String(255)) #活动类型
    begintime = db.Column(db.DateTime, default=datetime.datetime.now)  # 活动开始时间
    endtime = db.Column(db.DateTime, default=datetime.datetime.now)  # 活动结束时间
    updatetime = db.Column(db.DateTime, default=datetime.datetime.now)  # 活动上传时间
    stoptime= db.Column(db.DateTime, default=datetime.datetime.now)  # 活动报名截止时间
    main=db.Column(db.Text)#活动内容
    status = db.Column(db.Integer,default=0)#状态，0创建，1驳回，2通过，3删除
    userid = db.Column(db.Integer, db.ForeignKey('user.id'))#外键
    datas = db.relationship('Data', secondary=AD, backref=db.backref('adatas', lazy='dynamic'))
    aus = db.relationship('AU', backref='aus')  # AU外键

    def __repr__(self):
        return self

#表 3文件表
class Data(db.Model):
    __tablename__='data'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)  # 文件id
    name = db.Column(db.String(255))#原始文件名
    type=db.Column(db.String(255))#文件类型，‘music’或’video’或’image’或’pdf’或’word’
    path=db.Column(db.String(255))#文件路径
    newname=db.Column(db.String(255))#新文件名

    def __repr__(self):
        return self

#表 8用户申报文件表(用户申报编号,文件id)
UDCD=db.Table('dcud',db.Column('udcid', db.Integer, db.ForeignKey('udeclare.id')),db.Column('dataid', db.Integer, db.ForeignKey('data.id')))

#表 7用户申报表
class UDeclare(db.Model):
    __tablename__='udeclare'
    id=db.Column(db.Integer, primary_key=True, autoincrement=True)#用户申报编号
    userid=db.Column(db.Integer, db.ForeignKey('user.id'))#用户编号
    uptime=db.Column(db.DateTime, default=datetime.datetime.now)#提交时间
    type=db.Column(db.Integer,default=0)#状态，0或1
    datas=db.relationship('Data', secondary=UDCD, backref=db.backref('udcdatas', lazy='dynamic'))

    def __repr__(self):
        return self

#表 9用户申报记录表(申报任务编号,用户申报编号)
DUDC=db.Table('dudc',db.Column('declareid',db.Integer, db.ForeignKey('declare.id')),db.Column('udcid',db.Integer, db.ForeignKey('udeclare.id')))

#表 6申报任务表
class Declare(db.Model):
    __tablename__='declare'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)  # 申报id
    name = db.Column(db.String(255))  # 申报名
    begintime = db.Column(db.DateTime, default=datetime.datetime.now)  # 申报开始时间
    endtime = db.Column(db.DateTime, default=datetime.datetime.now)  # 申报结束时间
    main = db.Column(db.Text)  # 申报内容
    udeclares=db.relationship('UDeclare', secondary=DUDC, backref=db.backref('udcs', lazy='dynamic'))

    def __repr__(self):
        return self

#表 12用户申请培训文件表(用户申请培训编号，文件id)
UTD=db.Table('utd',db.Column('utid', db.Integer, db.ForeignKey('utrain.id')),db.Column('dataid', db.Integer, db.ForeignKey('data.id')))

#表 11用户申请培训表
class UTrain(db.Model):
    __tablename__='utrain'
    id=db.Column(db.Integer, primary_key=True, autoincrement=True)#用户申请培训编号
    userid=db.Column(db.Integer, db.ForeignKey('user.id'))#用户编号
    uptime=db.Column(db.DateTime, default=datetime.datetime.now)#提交时间
    type=db.Column(db.Integer,default=0)#状态，0或1
    datas=db.relationship('Data', secondary=UTD, backref=db.backref('utdatas', lazy='dynamic'))

    def __repr__(self):
        return self

TUT=db.Table('tut',db.Column('trainid',db.Integer, db.ForeignKey('train.id')),db.Column('utid',db.Integer, db.ForeignKey('utrain.id')))

#表 10能力提升培训表
class Train(db.Model):
    __tablename__ = 'train'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)  # 培训id
    name = db.Column(db.String(255))  # 培训名
    begintime = db.Column(db.DateTime, default=datetime.datetime.now)  # 培训开始时间
    endtime = db.Column(db.DateTime, default=datetime.datetime.now)  # 培训结束时间
    main = db.Column(db.Text)  # 培训内容
    utrains = db.relationship('UTrain', secondary=TUT, backref=db.backref('tuts', lazy='dynamic'))

    def __repr__(self):
        return self

#表 14用户分数表(用户编号,年份,分数)
class Score(db.Model):
    __tablename__="score"
    userid=db.Column(db.Integer,db.ForeignKey('user.id'),primary_key=True)
    year=db.Column(db.Integer,default=int(datetime.datetime.now().strftime('%Y')),primary_key=True)
    score=db.Column(db.Integer)

    def __repr__(self):
        return self

#表 15系统设置表(次数)
class System(db.Model):
    __tablename__='system'
    type=db.Column(db.String(255),primary_key=True)#类型
    main=db.Column(db.String(255))#内容

    def __repr__(self):
        return self

#表 16用户报告文件表(用户报告编号,文件id)
RD=db.Table('rd',db.Column('rid', db.Integer, db.ForeignKey('record.id')),db.Column('dataid', db.Integer, db.ForeignKey('data.id')))

#表 17用户报告表
class Record(db.Model):
    __tablename__='record'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)  # 报告id
    userid = db.Column(db.Integer, db.ForeignKey('user.id'))  # 用户编号
    year = db.Column(db.Integer, default=int(datetime.datetime.now().strftime('%Y')))  # 年份
    name = db.Column(db.String(255))  # 报告名
    datas = db.relationship('Data', secondary=RD, backref=db.backref('rdatas', lazy='dynamic'))

    def __repr__(self):
        return self
