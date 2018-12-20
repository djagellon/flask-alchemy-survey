from flask import render_template, url_for
from flask_user import login_required, current_user
from app.main import bp
from app.api import report, users
from app.api.errors import error_response

@bp.route('/')
@bp.route('/index')
@login_required
def index():
    r = report.get_user_reports().json

    return render_template('dashboard.html', data=r['data'], overall=r['overall'])


@bp.route('/dashboard')
def dashboard():
    
    r = report.get_user_reports().json

    return render_template('dashboard.html', data=r['data'], overall=r['overall'])
    

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
