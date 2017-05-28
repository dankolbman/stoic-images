import os
basedir = os.path.abspath(os.path.dirname(__file__))


class Config:
    HOST = '0.0.0.0'
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'hard to guess string'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_DATABASE_URI = os.environ.get('SQLALCHEMY_DATABASE_URI',
                                             'postgres://postgres:5432/stoic')
    CELERY_BROKER_URL = os.environ.get('CELERY_BROKER_URL',
                                       'redis://localhost:6379/0')
    CELERY_BACKEND = os.environ.get('CELERY_BACKEND',
                                    'redis://localhost:6379/0')
    CELERY_RESULT_BACKEND = os.environ.get('CELERY_RESULT_BACKEND',
                                           'redis://localhost:6379/0')
    IMAGE_UPLOAD_DIR = os.environ.get('IMAGE_UPLOAD_DIR',
                                      os.path.join(basedir, 'image_uploads'))
    MAX_CONTENT_LENGTH = 32 * 1024 * 1024
    ALLOWED_IMAGES = ['jpg', 'jpeg', 'png', 'gif' ]
    GEO_URL = 'http://geo/'

    @staticmethod
    def init_app(app):
        pass


class DevelopmentConfig(Config):
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = 'postgres:///stoic_dev'
    CELERY_ALWAYS_EAGER = True
    GEO_URL = 'http://localhost:8081/api/geo/'


class TestingConfig(Config):
    TESTING = True
    SECRET_KEY = 'secret'
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = 'postgres:///stoic_test'
    CELERY_ALWAYS_EAGER = True
    SERVER_NAME = 'localhost'
    GEO_URL = 'http://localhost:8081/api/geo/'


class ProductionConfig(Config):

    @classmethod
    def init_app(cls, app):
        Config.init_app(app)

        # email errors to the administrators
        import logging
        from logging.handlers import SMTPHandler
        credentials = None
        secure = None


class UnixConfig(ProductionConfig):
    @classmethod
    def init_app(cls, app):
        ProductionConfig.init_app(app)

        # log to syslog
        import logging
        from logging.handlers import SysLogHandler
        syslog_handler = SysLogHandler()
        syslog_handler.setLevel(logging.WARNING)
        app.logger.addHandler(syslog_handler)


config = {
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    'production': ProductionConfig,
    'unix': UnixConfig,

    'default': DevelopmentConfig
}
