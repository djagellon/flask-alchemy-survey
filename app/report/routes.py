from flask import Blueprint, render_template
from app import db
from app.report import bp

from app.models import SurveyModel

@bp.route('/report/')
def show_report():

    data = db.session.query(SurveyModel).all() 

    return render_template('reports.html', data=data)

@bp.route('/delete')
def delete_all():
    data = db.session.query(SurveyModel).all() 

    for s in data:
        db.session.delete(s)

    db.session.commit()
    return redirect(url_for('report.show_report'))
