from flask import Blueprint, render_template, redirect, url_for
from flask_user import login_required, roles_required
from app import db
from app.report import bp
from app.api import report, users

from app.models import SurveyModel

@bp.route('/report/all')
@roles_required('admin')
def show_all_reports():
    data = report.admin_all_reports()

    return render_template('reports_all.html', title="report", data=data.json)

@bp.route('/report/full/<module>/<answer>')
@login_required
def show_full_output(module, answer):

    if users.has_full_access():
        data = report.get_output('long', module, answer)
        return render_template('report_full.html', data=data.json)

    return render_template('report_unlock.html')


@bp.route('/report/<module>')
@login_required
def show_report(module):
    data = report.get_answer_for_module(module)

    return render_template('reports.html', title="report", data=data.json, module=module)

@bp.route('/delete')
@roles_required('admin')
def delete_all():
    data = db.session.query(SurveyModel).all() 

    for s in data:
        db.session.delete(s)

    db.session.commit()
    return redirect(url_for('report.show_all_reports'))
