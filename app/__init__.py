import os

from flask import Flask, request, current_app
from config import Config
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate

db = SQLAlchemy()
migrate = Migrate()

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    db.init_app(app)
    migrate.init_app(app, db)

    from report.report import bp as bp_report
    app.register_blueprint(bp_report)

    from collect.survey import bp as bp_survey
    app.register_blueprint(bp_survey)

    db.init_app(app)

    return app

from app import models