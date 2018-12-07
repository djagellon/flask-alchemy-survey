from flask import render_template, url_for
from flask_user import login_required, current_user
from app.main import bp
from app.api import report, users
from app.api.errors import error_response

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

@bp.route('/profile', defaults={'username': None})
@bp.route('/profile/<username>')
@login_required
def profile(username=None):

    not_self = username and current_user.username != username

    # Non-Admins will always see their own profile
    if not_self and not current_user.is_admin:
        username = None

    user = users.get_user_by_username(username)

    return render_template('profile.html', user=user.json)
