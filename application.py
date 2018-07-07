# from sqlalchemy import create_engine
# from sqlalchemy.orm import sessionmaker, scoped_session
# from database_setup import Base, Restaurant, MenuItem

from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
from wtforms import StringField, BooleanField, RadioField, FieldList, FormField, SubmitField
from wtforms.meta import DefaultMeta
from flask_wtf import FlaskForm
import json


app = Flask(__name__)

@app.route('/')
@app.route('/home')
def show_home():
  return render_template('home.html')

@app.route('/collect/<survey>/')
def collect(survey):
  print "COLLECTING DATA FROM: %s" % survey

  try:
    with open('surveys/%s.json' % survey) as f:
      data_string = json.load(f)
  except IOError:
    return "SURVEY NOT FOUND: %s" % name


  page = get_surveys_per_page(data_string)
  submit_string = 'Continue'

  print "SURVEY STRUCT: %s" % page


  return render_template('question.html', survey=page, submit_string=submit_string)

def get_surveys_per_page(page):
  """
  Begin collecting data one page at a time
  """
  pages = [p for p in page] 

  survey = build_survey_object(pages[0])

  # import pdb;pdb.set_trace()
  return survey

def build_survey_object(data):
  questions = [build_question(q) for q in data] 

  return questions

class BindNameMeta(DefaultMeta):

  def bind_field(self, form, unbound_field, options):
    # allows us to overvide the name attribute of the field
    if 'custom_name' in unbound_field.kwargs:
      options['name'] = unbound_field.kwargs.pop('custom_name')
    return unbound_field.bind(form=form, **options)

class PageForm(FlaskForm):
  pass

def build_question(question):
  # This ist he suggested way to create dynamic forms according to docs:
  # http://wtforms.simplecodes.com/docs/1.0.1/specific_problems.html#dynamic-form-composition
  import importlib

  class DynamicForm(FlaskForm):
    Meta = BindNameMeta


  question_type ='%sField' % question['type'].capitalize() 
  FieldClass = globals()[question_type]

  choices = [(a['label'], a['text']) for a in question['answers']]
  label = question['label']

  DynamicForm.question = FieldClass(question['title'], choices=choices, custom_name=label)
  # DynamicForm.submit = SubmitField('Continue')

  form = DynamicForm()
  return form

if __name__ == '__main__':
  app.secret_key = 'supersecretkey'
  app.debug = True
  app.run(host = '0.0.0.0', port = 5000)

