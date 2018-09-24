from flask import render_template, url_for
from flask_user import login_required, current_user
from app.main import bp
from app.api import report

@bp.route('/')
@bp.route('/index')
@login_required
def index():
    data = report.get_user_reports()

    return render_template('dashboard.html', data=data.json)

@bp.route('/dashboard')
def dashboard():
    
    data = report.get_user_reports()

    return render_template('dashboard.html', data=data.json)
