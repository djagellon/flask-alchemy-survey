# from sqlalchemy import create_engine
# from sqlalchemy.orm import sessionmaker, scoped_session
# from database_setup import Base, Restaurant, MenuItem

from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
from wtforms import StringField, BooleanField, RadioField, FieldList, FormField, SubmitField
from wtforms.meta import DefaultMeta
from wtforms.validators import Required
from flask_wtf import FlaskForm
from config import Config
from app import db
import json

from app.models import SurveyModel

app = Flask(__name__)
app.config.from_object(Config)

IGNORE_FIELDS = set('csrf_token submit'.split())

@app.route('/')
@app.route('/home')
def show_home():
    return render_template('home.html')

@app.route('/collect/survey/', defaults={'page': None}, methods=['GET', 'POST'])
@app.route('/collect/survey/<page>', methods=['GET', 'POST'])
def collect(page):

    # checks pagerunner for page index
    # determine logic for page
        # skip page based on logic
    print "PAGE: %s" % page
    print "REQUEST: %s" % request

    page = int(page) if page else None
    form = get_surveys_per_page(page)

    if form and form.errors:
        print "FORM ERRORS? %s" % form.errors

    if form and form.validate_on_submit():
        # add data to db

        # db.session.add(s)
        # db.session.commit()

        # answers = [(k, v) for k, v in form.data.items() if k not in IGNORE_FIELDS]
        pairs = ((k, v) for k, v in form.data.items() if k not in IGNORE_FIELDS)

        for question, a in form.data.items():
            if question not in IGNORE_FIELDS:
                cls = getattr(SurveyModel, '{}'.format(question))
                kw = {question: a}
                import pdb;pdb.set_trace()
                db.session.add(cls(**kw))

        db.session.commit()

        # form = get_surveys_per_page(page + 1)
        return redirect(url_for('collect', page=page+1))

    # import pdb;pdb.set_trace()
    print "NOW LOADING FORM: %s" % form
    return render_template('question.html', form=form)

def get_surveys_per_page(page):
    """
    Begin collecting data one page at a time
    """
    # get next page
    next_form = 'SurveyForm%s' % page

    if page == 0:
        return None

    try:
        SurveyClass = globals()[next_form]
        page = SurveyClass()
    except KeyError:
        page = FinalForm()

    return page

class SurveyForm(FlaskForm):
    submit = SubmitField('Continue')

class SurveyForm1(SurveyForm):
    q1 = RadioField("Where does information Security reside within the organization?",
        choices = [
            ("IT", "Information Technology"),
            ("RM", "Risk Managment"),
            ("EM", "Executive Management"),
            ("F", "Finanace"),
            ("ISD", "Informatin Security Department or Division within Information Technology"),
        ])

    q2 = RadioField("Does the organization have budget and resources dedicated to information security?",
        choices = [
            ("Y", "Yes"),
            ("N", "No"),
        ])

class SurveyForm2(SurveyForm):
    q2a = StringField("What percentage of the IT budget is set for information security?")
    q2b = StringField("What percentage of the organizational budget is set for information security?")


class FinalForm(FlaskForm):
    agreement = BooleanField("Thank you for completeing the survey. By clicking the checkbox you agree to our terms.")
    submit = SubmitField('Finish')

if __name__ == '__main__':
    app.debug = True
    app.run(host = '0.0.0.0', port = 5000)
