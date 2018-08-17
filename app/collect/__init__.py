from flask import Blueprint

bp = Blueprint('survey', __name__, template_folder='templates')

from app.collect import survey
