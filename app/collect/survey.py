from app import db
from flask_user import current_user
from wtforms import Form, widgets, StringField, TextAreaField, BooleanField, FieldList, IntegerField, RadioField, SelectField, FormField, SubmitField, SelectMultipleField
from wtforms.meta import DefaultMeta
from flask_wtf import FlaskForm
from datetime import datetime

import logging as log
import json

from app.models import User, SurveyModel, QuestionModel

log.basicConfig(level=log.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

class BindNameMeta(DefaultMeta):

    def bind_field(self, form, unbound_field, options):
        # allows us to overvide the name attribute of the field
        if 'custom_name' in unbound_field.kwargs:
            options['name'] = unbound_field.kwargs.pop('custom_name')

        return unbound_field.bind(form=form, **options)

class TextField(StringField):
    pass

class TextareaField(TextAreaField):
    pass

class MultiField(SelectMultipleField):
    """
    A multiple-select

    Iterating the field will produce subfields, allowing custom rendering of
    the enclosed checkbox fields.
    """
    widget = widgets.ListWidget(prefix_label=False)
    option_widget = widgets.CheckboxInput()

class Survey(object):

    def __init__(self, module):
        self.module = module
        self.page_index = 0
        self.progress = 1
        self.questions = self.load_survey()
        self.survey_length = len(self.questions)
        self.survey_db = self.get_surveyModel(module)

    def get_surveyModel(self, module):
        # search users db for the survey
        # create one if does not exist
        user = User.query.get_or_404(current_user.id)
        survey = user.surveys.filter_by(module=module).one_or_none()

        if survey:
            # update page index and progress based on questions answered
            self.page_index = len(survey.questions.all())
            self.progress = (float(self.page_index) / float(self.survey_length)) * 100
            log.info("SURVEY IN PROGRESSS at page: %s" % self.page_index)
        else:
            survey = SurveyModel(module=module, user=user, started_on=datetime.now())
            db.session.add(survey)
            db.session.commit()

        return survey

    def load_survey(self):
        try:
            with open('surveys/%s.json' % self.module) as f:
                return json.load(f)
        except IOError as error:
            log.error("Survey File Not Found %s" % self.module)
            raise

    def show_question(self, cond):
        show = False

        if not cond or cond == 'all':
            return True

        cond_question, cond_answer = cond.split('.')

        # We need to query the db session and not the surveymodel
        # to prevent lazyload errors
        survey = db.session.query(SurveyModel).filter_by(id=self.survey_db.id).one() 

        #TODO: user one_or_none() when we ensured survey can only be taken once
        question = survey.questions.filter_by(label=cond_question).first()

        if question:
            show = cond in question.answer

        log.info("CONDITION: %s for ANSWERS: %s" % (show, cond))

        return show

    def get_questions(self):
        return self.questions[self.page_index]

    def add_answers(self, question, answer, question_type):

        data = QuestionModel(label=question, answer=answer, question_type=question_type, survey=self.survey_db)

        db.session.add(data)
        db.session.commit()

    def finish(self):
        self.survey_db.completed_on = datetime.now()
        db.session.add(self.survey_db)
        db.session.commit()

    def increment_page(self, page=None):
        if page:
            self.page_index = page 
        else:
            self.page_index += 1

        self.progress = (float(self.page_index) / float(self.survey_length)) * 100

    def is_complete(self):
        if self.page_index >= self.survey_length:
            self.finish()
            return True

        return False

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
                # Question is skipped based on previous answers
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
