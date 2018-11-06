from flask import Blueprint, flash, render_template, redirect, url_for
from flask_user import login_required, roles_required
from app import db
from app.report import bp
from app.api import report, users

from app.models import SurveyModel

import json, collections

@bp.route('/report/all')
@roles_required('admin')
def show_all_reports():
    data = report.admin_all_reports()

    return render_template('reports_all.html', title="report", data=data.json)

@bp.route('/report/full/<module>/<answer>')
@login_required
def show_full_output(module, answer):
    access = users.get_access()

    if access.json['admin']:
        data = report.get_output('long', module, answer)
        return render_template('report_full.html', data=data.json)

    return render_template('report_unlock.html')


@bp.route('/report/<module>')
@login_required
def show_report(module):
    data = report.get_answer_for_module(module)

    # retains order of objects
    obj = json.loads(data.data, object_pairs_hook=collections.OrderedDict)
    score = obj['score']
    grade = report.get_score_grade(score)

    return render_template('reports.html', title="report", 
        data=obj['answers'], module=module, score=score, grade=grade)

@bp.route('/report/delete', defaults={'module': None})
@bp.route('/report/delete/<module>')
@roles_required('admin')
def delete_survey(module=None):
    result = report.delete_survey(module)

    if result.json['success']:
        flash('Data erased.', 'info')
        
    return redirect(url_for('main.dashboard'))
