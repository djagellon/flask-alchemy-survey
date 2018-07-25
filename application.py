# from sqlalchemy import create_engine
# from sqlalchemy.orm import sessionmaker, scoped_session
# from database_setup import Base, Restaurant, MenuItem

from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
from wtforms import Form, widgets, StringField, BooleanField, FieldList, IntegerField, RadioField, SelectField, FormField, SubmitField, SelectMultipleField
from wtforms.meta import DefaultMeta
from wtforms.validators import Required
from flask_wtf import FlaskForm
from config import Config
from app import db
import json
import logging as log

from app.models import SurveyModel, QuestionModel


gv = {}

app = Flask(__name__)
app.config.from_object(Config)
db.init_app(app)

IGNORE_FIELDS = set('csrf_token submit'.split())

log.basicConfig(level=log.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

def has_open(value):
    return value.render_kw and value.render_kw.get('class') == 'other_option'

app.jinja_env.filters['has_open'] = has_open

@app.route('/')
@app.route('/home')
def show_home():
    return render_template('home.html')

@app.route('/report')
def show_report():

    data = db.session.query(SurveyModel).all() 

    return render_template('report.html', data=data)

class Survey(object):

    def __init__(self, module):
        self.questions = None
        self.page_index = 0
        self.module = module
        self.questions = self.load_survey()
        self.survey_length = len(self.questions)
        self.db = SurveyModel(module=module)

    def load_survey(self):
        try:
            log.debug("LOADING DATA FROM: %s" % self.module)
            with open('surveys/%s.json' % self.module) as f:
                return json.load(f)
        except IOError:
            log.debug("MODULE NOT FOUND: %s" % self.module)
            raise


@app.route('/collect/<module>/start')
def start(module):
    global gv

    gv['survey'] = Survey(module)

    return render_template('start.html')

@app.route('/collect/', methods=['GET', 'POST'])
def collect():
    global gv

    survey = gv['survey']

    form = build_form(survey.questions[survey.page_index])

    if form and form.validate_on_submit():
        survey.page_index += 1

        for question, answer in form.data.items():

            if answer and question not in IGNORE_FIELDS:
                # TODO: whats the shortcut for this?
                if not type(answer) is list:
                    answer = [answer]
                    
                q = QuestionModel(label=question, answer=answer)

                log.debug('Adding data to db: %s' % q)
                survey.db.questions.append(q)
                db.session.add(survey.db)

        if survey.page_index >= survey.survey_length:
            db.session.commit()
            # return render_template('endsurvey.html')
            return redirect(url_for('show_report'))

        form = build_form(survey.questions[survey.page_index])

    while not len(form._unbound_fields):
        # no fields in page, go to next page
        log.debug("***************** SKIPPPIING ***************** ")
        survey.page_index += 1
        try:
            form = build_form(survey.questions[survey.page_index])
        except IndexError:
            # return render_template('endsurvey.html')
            return redirect(url_for('show_report'))

    return render_template('survey.html', form=form)

class BindNameMeta(DefaultMeta):

    def bind_field(self, form, unbound_field, options):
        # allows us to overvide the name attribute of the field
        if 'custom_name' in unbound_field.kwargs:
            options['name'] = unbound_field.kwargs.pop('custom_name')

        return unbound_field.bind(form=form, **options)

class TextField(StringField):
    pass

class MultiField(SelectMultipleField):
    """
    A multiple-select, except displays a list of checkboxes.

    Iterating the field will produce subfields, allowing custom rendering of
    the enclosed checkbox fields.
    """
    widget = widgets.ListWidget(prefix_label=False)
    option_widget = widgets.CheckboxInput()

def show_question(cond):
    global gv
    survey = gv['survey']
    show = False

    if not cond or cond == 'all':
        return True

    cond_question, cond_answer = cond.split('.')
    questions = survey.db.to_dict().get('questions', [])
    question = filter(lambda qn: qn['label'] == cond_question, questions)

    try:
        show = question[0] and cond in question[0]['answer']
        # import pdb;pdb.set_trace()
    except IndexError:
        # question was not found for some reason
        # import pdb;pdb.set_trace()
        log.warn("Question not found when checking condition.")
        return True

    log.debug("CONDITION: %s" % show)
    return show

def build_form(questions):
    # This ist he suggested way to create dynamic forms according to docs:
    # http://wtforms.simplecodes.com/docs/1.0.1/specific_problems.html#dynamic-form-composition

    class DynamicForm(FlaskForm):
        Meta = BindNameMeta

    for question in questions:
        choices = []
        other_field = None
        other_label = None
        question_type ='%sField' % question['type'].capitalize() 
        FieldClass = globals()[question_type]
        label = question['label']

        if not show_question(question['condition']):
            continue 

        if len(question['answers']) > 1:
            for choice in question['answers']:
                choices.append((choice['label'], choice['text']))

                if choice.has_key('open'):
                    other_label = question['label'] + '_other'

            question_field = FieldClass(question['title'], choices=choices, custom_name=label)

        else:
            question_field = FieldClass(question['title'], custom_name=label)

        question_field.flags = {'other': False}

        setattr(DynamicForm, label, question_field)

        if other_label:
            setattr(DynamicForm, other_label, StringField(id=other_label, render_kw={'class': 'other_option'}))

    return DynamicForm()

if __name__ == '__main__':
  app.debug = True
  app.run(host = '0.0.0.0', port = 5000)
