from app.collect import bp
from app.collect.survey import Survey
from flask import render_template, redirect, url_for
from flask_user import login_required, current_user

import logging as log

IGNORE_FIELDS = set('csrf_token submit'.split())
gv = {}

log.basicConfig(level=log.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

@bp.route('/collect/<module>/start')
@login_required
def start(module):
    # TODO: Once user registration is implemented...
    # - Check for existing Survey in the db
    # - Create one if it does not exist
    global gv
    gv['survey'] = Survey(module)

    return render_template('start.html')

@bp.route('/collect/', methods=['GET', 'POST'])
def collect():
    global gv
    survey = gv['survey']

    form = survey.get_page()

    if form and form.validate_on_submit():
        survey.increment_page()

        for question, answer in form.data.items():

            if answer and question not in IGNORE_FIELDS:
                if not type(answer) is list:
                    answer = [answer]

                survey.add_answers(question, answer)

        if survey.is_complete():
            return redirect(url_for('survey.end_survey', module=survey.module))

        form = survey.get_page()

    while not len(form._unbound_fields):
        # no fields in page form, go to next page
        log.debug("skipped page -- no fields")
        survey.increment_page()

        if survey.is_complete():
            return redirect(url_for('survey.end_survey', module=survey.module))

        form = survey.get_page()

    return render_template('survey.html', form=form)

@bp.route('/collect/<module>/end')
@login_required
def end_survey(module):

    return render_template('endsurvey.html', module=module)
