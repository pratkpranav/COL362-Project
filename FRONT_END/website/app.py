from flask import Flask
from os import path
from flask_login import LoginManager
from website.database import get_database_connection, db_get_user_with_handle
import logging
import configparser
import website


#Read the configuration file
website.parser = configparser.ConfigParser(allow_no_value=True)
website.parser.read('config.cfg')

#Set the log file
logging.basicConfig(format = 'Line No. : %(lineno)d - %(message)s',level = logging.DEBUG, filename = website.parser['logInfo']['output_file'])

#TODO: make a config file storing the details
#      of database
host = website.parser['dbInfo']['host']
port = int(website.parser['dbInfo']['port'])
databaseName = website.parser['dbInfo']['name']
databaseUser = website.parser['dbInfo']['user']
databasePass = website.parser['dbInfo']['password']

logging.debug("Database Host: %s", host)
logging.debug("Database Port: %s", port)
logging.debug("Database Name: %s", databaseName)
logging.debug("Database User: %s", databaseUser)
logging.debug("Database Password: %s", databasePass)


website.login_manager = LoginManager()
website.login_manager.login_view = 'auth.login'

def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = 'qwernaowja'
    app.config['UPLOAD_EXTENSIONS'] = ['.jpg', '.png']
    app.config['UPLOAD_PATH'] = 'static/'

    from .views import views
    from .auth import auth

    app.register_blueprint(views, url_prefix='/')
    app.register_blueprint(auth, url_prefix='/')

    website.login_manager.init_app(app)

    website.db, website.dbConn = get_database_connection(host, port, databaseName, databaseUser, databasePass )

    assert website.db != None
    assert website.dbConn != None

    @website.login_manager.user_loader
    def load_user(handle):
        user = db_get_user_with_handle(website.db, website.dbConn, handle)
        if user is None:
            return user
        return website.User(user, handle == "col362_ta")

    return app

