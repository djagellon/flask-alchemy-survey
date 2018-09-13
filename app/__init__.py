import os

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

    return app

from app import models