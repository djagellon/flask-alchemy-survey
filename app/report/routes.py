from flask import Blueprint, render_template, redirect, url_for
from flask_login import login_required
from flask_user import roles_required
from app import db
from app.report import bp

from app.models import SurveyModel

@bp.route('/report/all')
@roles_required('admin')
def show_all_reports():
    data = db.session.query(SurveyModel).all() or []
    return render_template('reports_all.html', title="report", data=data)

@bp.route('/report/<module>')
@login_required
def show_report(module):
    # data = db.session.query(SurveyModel).all() 
    return render_template('reports.html', title="report", module=module)

@bp.route('/delete')
@login_required
def delete_all():
    data = db.session.query(SurveyModel).all() 

    for s in data:
        db.session.delete(s)

    db.session.commit()
    return redirect(url_for('report.show_all_reports'))
