#!/usr/bin/env python
import os
from app import create_app, db
from app.models.models import User,AD,AU,Activity,Data,UDCD,UDeclare,DUDC,Declare,UTD,UTrain,TUT,Train,Score,System,RD,Record
from flask_script import Manager, Shell
from flask_migrate import Migrate, MigrateCommand
app = create_app(os.getenv('FLASK_CONFIG') or 'default')
manager = Manager(app)
migrate = Migrate(app, db)
from flask_cors import CORS
def make_shell_context():
    return dict(app=app, db=db, User=User,AD=AD,AU=AU,Activity=Activity,Data=Data,UDCD=UDCD,UDeclare=UDeclare,DUDC=DUDC,Declare=Declare,UTD=UTD,UTrain=UTrain,TUT=TUT,Train=Train,Score=Score,System=System,RD=RD,Record=Record)
manager.add_command("shell", Shell(make_context=make_shell_context))
manager.add_command('db', MigrateCommand)

if __name__ == '__main__':
    CORS(app, resources={r"/*": {"origins": "*"}})
    manager.run()
    