from app import db
from flask import Blueprint, render_template, redirect, url_for
from wtforms import Form, widgets, StringField, BooleanField, FieldList, IntegerField, RadioField, SelectField, FormField, SubmitField, SelectMultipleField
from wtforms.meta import DefaultMeta
from wtforms.validators import Required
from flask_wtf import FlaskForm

import logging as log
import json

from app.models import SurveyModel, QuestionModel

gv = {}

bp = Blueprint('survey', __name__, template_folder='templates')

IGNORE_FIELDS = set('csrf_token submit'.split())

log.basicConfig(level=log.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

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

    def show_question(self, cond):
        show = False

        if not cond or cond == 'all':
            return True

        cond_question, cond_answer = cond.split('.')
        questions = self.db.to_dict().get('questions', [])
        question = filter(lambda qn: qn['label'] == cond_question, questions)

        try:
            show = question[0] and cond in question[0]['answer']
        except IndexError:
            # question was not found for some reason
            log.warn("Question not found when checking condition: [%s]." % cond)
            return True

        log.debug("CONDITION: %s" % show)
        return show

    def get_questions(self):
        return self.questions[self.page_index]

    def add_answers(self, data):
        self.db.questions.append(data)        
        db.session.add(self.db)

    def finish(self):
        db.session.commit()

    def increment_page(self, page=None):
        if page:
            self.page_index = page 
        else:
            self.page_index += 1

    def get_page(self):
    # This is the suggested way to create dynamic forms according to docs:
    # http://wtforms.simplecodes.com/docs/1.0.1/specific_problems.html#dynamic-form-composition

        class DynamicForm(FlaskForm):
            Meta = BindNameMeta

        questions = self.get_questions()

        for question in questions:
            choices = []
            other_field = None
            other_label = None
            question_type ='%sField' % question['type'].capitalize() 
            FieldClass = globals()[question_type]
            label = question['label']

            if not self.show_question(question['condition']):
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

@bp.route('/collect/<module>/start')
def start(module):
    # TODO: Once user registration is implemented...
    # - Check for existing Survey in the db
    # - Create one if it does not exist
    global gv
    gv['survey'] = Survey(module)

    return render_template('start.html')

@bp.route('/collect/', methods=['GET', 'POST'])
def collect(module=None):
    # TODO: Once user registration is implemented...
    # - Retrive survey from db
    global gv
    survey = gv['survey']

    form = survey.get_page()

    if form and form.validate_on_submit():
        survey.increment_page()

        for question, answer in form.data.items():

            if answer and question not in IGNORE_FIELDS:
                # TODO: whats the shortcut for this?
                if not type(answer) is list:
                    answer = [answer]
                    
                question_data = QuestionModel(label=question, answer=answer)
                survey.add_answers(question_data)

        if survey.page_index >= survey.survey_length:
            survey.finish()
            # return render_template('endsurvey.html')
            return redirect(url_for('report.show_report'))

        form = survey.get_page()

    while not len(form._unbound_fields):
        # no fields in page, go to next page
        log.debug("***************** SKIPPPIING ***************** ")
        survey.increment_page()
        try:
            form = survey.get_page()
        except IndexError:
            # return render_template('endsurvey.html')
            return redirect(url_for('report.show_report'))

    return render_template('survey.html', form=form)
