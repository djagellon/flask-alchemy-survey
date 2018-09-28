import os
import logging

from logging.handlers import RotatingFileHandler, SMTPHandler
from flask import Flask, request, current_app
from flask_bootstrap import Bootstrap
from config import Config
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_user import UserManager

db = SQLAlchemy()
migrate = Migrate()

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    bootstrap = Bootstrap(app)

    db.init_app(app)
    migrate.init_app(app, db)

    from app.models import User
    user_manager = UserManager(app, db, User)

    from app.errors import bp as errors_bp
    app.register_blueprint(errors_bp)

    from app.api import bp as bp_api
    app.register_blueprint(bp_api, url_prefix='/api')

    from app.main import bp as bp_main
    app.register_blueprint(bp_main)

    from app.report import bp as bp_report
    app.register_blueprint(bp_report)

    from app.collect import bp as bp_survey
    app.register_blueprint(bp_survey)
    
    @app.context_processor
    def context_processor():
        return dict(user_manager=user_manager)

    if not app.debug:
        if not os.path.exists('logs'):
            os.mkdir('logs')

        file_handler = RotatingFileHandler('logs/vera.log', maxBytes=10240, backupCount=10)

        file_handler.setFormatter(logging.Formatter(
            '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'))

        file_handler.setLevel(logging.INFO)
        app.logger.addHandler(file_handler)

        app.logger.setLevel(logging.INFO)
        app.logger.info('Vera startup')
        
        if app.config['MAIL_SERVER']:
            auth = None

            if app.config['MAIL_USERNAME'] or app.config['MAIL_PASSWORD']:
                auth = (app.config['MAIL_USERNAME'], app.config['MAIL_PASSWORD'])
            secure = None

            if app.config['MAIL_USE_TLS']:
                secure = ()

            mail_handler = SMTPHandler(
                mailhost=(app.config['MAIL_SERVER'], app.config['MAIL_PORT']),
                fromaddr='no-reply@' + app.config['MAIL_SERVER'],
                toaddrs=app.config['ADMINS'], subject='Vera Strategic Failure',
                credentials=auth, secure=secure)

            mail_handler.setLevel(logging.ERROR)
            app.logger.addHandler(mail_handler)

    return app

from app import models