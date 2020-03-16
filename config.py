import os
basedir = os.path.abspath(os.path.dirname(__file__))

class Config(object):

    # app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://{}:{}@{}/{}'.format(
    # os.getenv('DB_USER', 'flask'),
    # os.getenv('DB_PASSWORD', ''),
    # os.getenv('DB_HOST', 'mysql'),
    # os.getenv('DB_NAME', 'flask')
    # )

    # SECRET_KEY = environ.get('SECRET_KEY')
    # FLASK_APP = environ.get('FLASK_APP')
    # FLASK_ENV = environ.get('FLASK_ENV')
    
    #DB_USER = environ.get('DB_USER')
    #DB_PASSWORD = environ.get('DB_PASSWORD')   
    #DB_HOST = environ.get('DB_HOST')
    #DB_NAME = environ.get('DB_NAME')    
    
    #SQLALCHEMY_DATABASE_URI = environ.get("SQLALCHEMY_DATABASE_URI")
    SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://{}:{}@{}/{}'.format(
    os.getenv('DB_USER', 'flask'),
    os.getenv('DB_PASSWORD', ''),
    os.getenv('DB_HOST', 'mysql'),
    os.getenv('DB_NAME', 'flask')
    )