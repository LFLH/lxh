from app import db
import datetime

class User(db.Model):
    __tablename__ = 'user'
    id=db.Column(db.Integer, primary_key=True,autoincrement=True )#系统id
    username=db.Column(db.String(255))#统一社会信息代码
    name=db.Column(db.String(255))#科普基地单位名称
    password=db.Column(db.String(255))#口令
    type=db.Column(db.String(255))#sysadmin或user
    updatetime=db.Column(db.DateTime,default=datetime.datetime.now)#最后操作更新时间
    checked = db.Column(db.Integer, default=0)#0为有效申报用户，1为正常用户
    users = db.relationship('Activity', backref='user')

    def __repr__(self):
        return self

AD=db.Table('ad',db.Column('activityid',db.Integer,db.ForeignKey('activity.id')),db.Column('dataid',db.Integer,db.ForeignKey('data.id')))

class Activity(db.Model):
    __tablename__ = 'activity'
    id=db.Column(db.Integer, primary_key=True,autoincrement=True )
    name=db.Column(db.String(255))
    begintime=db.Column(db.DateTime,default=datetime.datetime.now)
    endtime=db.Column(db.DateTime,default=datetime.datetime.now)
    cxtime=db.Column(db.DateTime)
    uptime=db.Column(db.DateTime,default=datetime.datetime.now)
    main=db.Column(db.Text)
    type=db.Column(db.String(255))
    status = db.Column(db.String(255),default="undelete")
    userid=db.Column(db.Integer, db.ForeignKey('user.id'))
    datas = db.relationship('Data', secondary=AD, backref=db.backref('datas', lazy='dynamic'))

    def __repr__(self):
        return self

class Data(db.Model):
    __tablename__ = 'data'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    '''music,video,image'''

    type=db.Column(db.String(255))
    data=db.Column(db.String(255))

    def __repr__(self):
        return self
