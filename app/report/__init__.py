from flask import Blueprint

bp = Blueprint('report', __name__, template_folder='templates')

from app.report import routes
