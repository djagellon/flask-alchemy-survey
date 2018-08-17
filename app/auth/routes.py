from flask import render_template
from forms import LoginForm
from app import db
from app.auth import bp

@bp.route('/login/')
def login():
    form = LoginForm()
    return render_template('login.html', title='Sign In', form=form)