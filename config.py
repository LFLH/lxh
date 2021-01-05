# 系统的配置信息
import os
basedir = os.path.abspath(os.path.dirname(__file__))


class Config:
    SECRET_KEY = 'key'
    SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://root:@localhost/lxh'
    # 'mysql+mysqlconnector://root:123456@39.96.44.243/teach_achievement'
    # 反向生成models.py : sqlacodegen mysql+mysqlconnector://root:@127.0.0.1/teach_achievement > new_models.py
    SQLALCHEMY_COMMIT_ON_TEARDOWN = True
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    @staticmethod
    def init_app(app):
        pass


class DevelopmentConfig(Config):
    pass


class TestingConfig(Config):
    pass


class ProductionConfig(Config):
    pass

# config字典注册了不同配置环境
config = {
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}


# if __name__ == '__main__':
#     print(basedir)