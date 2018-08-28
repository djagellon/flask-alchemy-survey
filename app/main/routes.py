from flask import render_template, url_for
from app.main import bp

@bp.route('/')
@bp.route('/index')
def index():
    return render_template('home.html')
