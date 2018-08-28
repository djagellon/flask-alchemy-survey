from flask import Blueprint, render_template, redirect, url_for
from flask_login import login_required
from app import db
from app.report import bp

from app.models import SurveyModel

@bp.route('/report/')
@login_required
def show_report():

    data = db.session.query(SurveyModel).all() 

    return render_template('reports.html', title="Report", data=data)

@bp.route('/delete')
@login_required
def delete_all():
    data = db.session.query(SurveyModel).all() 

    for s in data:
        db.session.delete(s)

    db.session.commit()
    return redirect(url_for('report.show_report'))
