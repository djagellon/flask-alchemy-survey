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

from app.models import SurveyModel, QuestionModel

gv = {}

app = Flask(__name__)
app.config.from_object(Config)
db.init_app(app)

IGNORE_FIELDS = set('csrf_token submit'.split())

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
            print "LOADING DATA FROM: %s" % self.module
            with open('surveys/%s.json' % self.module) as f:
                return json.load(f)
        except IOError:
            print "MODULE NOT FOUND: %s" % self.module
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

    # import pdb;pdb.set_trace()
    if form and form.validate_on_submit():
        survey.page_index += 1

        for question, answer in form.data.items():

            if question not in IGNORE_FIELDS:
                # whats the shortcut for this?
                if not type(answer) is list:
                    answer = [answer]
                    
                q = QuestionModel(label=question, answer=answer)
                survey.db.questions.append(q)
                db.session.add(survey.db)

        if survey.page_index >= survey.survey_length:
            # import pdb;pdb.set_trace()
            db.session.commit()
            # return render_template('endsurvey.html')
            return redirect(url_for('show_report'))

        form = build_form(survey.questions[survey.page_index])

    return render_template('survey.html', form=form)

class BindNameMeta(DefaultMeta):

    def bind_field(self, form, unbound_field, options):
        # allows us to overvide the name attribute of the field
        if 'custom_name' in unbound_field.kwargs:
            options['name'] = unbound_field.kwargs.pop('custom_name')

        return unbound_field.bind(form=form, **options)

class OpenForm(Form):
    """
    Adds an open text field to a specified choice within RadioFields 
    """
    # import pdb;pdb.set_trace()
    # widget = widgets.ListWidget(prefix_label=False)
    # option_widget = widgets.IntegerRangeField()
    r = RadioField('some question ahppening', choices=[('one', 'one'), ('two', 'two'), ('other', 'other')], render_kw={'class':"hasopen"})
    sometext = StringField(render_kw={'class':"hasopen"})

class OptForm(Form):
    first_name = StringField('DUMMY')
    openform = FormField(OpenForm)

@app.route('/widget/')
def widget():
    form = OpenForm() 
    form.r.flags.open = True
    # import pdb;pdb.set_trace()
    return render_template('question.html', form=form)

class MultiField(SelectMultipleField):
    """
    A multiple-select, except displays a list of checkboxes.

    Iterating the field will produce subfields, allowing custom rendering of
    the enclosed checkbox fields.
    """
    widget = widgets.ListWidget(prefix_label=False)
    option_widget = widgets.CheckboxInput()

def build_form(questions):
    # This ist he suggested way to create dynamic forms according to docs:
    # http://wtforms.simplecodes.com/docs/1.0.1/specific_problems.html#dynamic-form-composition
    import importlib

    class DynamicForm(FlaskForm):
        Meta = BindNameMeta

    for question in questions:
        choices = []
        question_type ='%sField' % question['type'].capitalize() 
        FieldClass = globals()[question_type]
        label = question['label']

        # import pdb;pdb.set_trace()
        if question['answers']:
            choices = [(a['label'], a['text']) for a in question['answers']]
            question_field = FieldClass(question['title'], choices=choices, custom_name=label)
        else:
            question_field = FieldClass(question['title'], custom_name=label)

        setattr(DynamicForm, label, question_field)

    form = DynamicForm()
    return form

if __name__ == '__main__':
  app.debug = True
  app.run(host = '0.0.0.0', port = 5000)
