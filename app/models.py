from app import db
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from flask_user import UserMixin

class User(db.Model, UserMixin):
    __tablename__ = 'user'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), index=True, unique=True)
    email = db.Column(db.Unicode(255), nullable=False, index=True, unique=True)
    # email_confirmed_at = db.Column(db.DateTime())

    password = db.Column(db.String(255), nullable=False, server_default='')
    active = db.Column(db.Boolean(), server_default='0')

    surveys = db.relationship('SurveyModel', backref='user', lazy='dynamic')
    roles = db.relationship('Role', secondary='user_roles', backref=db.backref('user', lazy='dynamic'))

    def __repr__(self):
        return '<User {}>'.format(self.username)

    def to_dict(self):
        return dict(id = self.id,
                    username = self.username,
                    email = self.email,
                    roles = self.roles)

class Role(db.Model):
    __tablename__ = 'roles'
    id = db.Column(db.Integer(), primary_key=True)
    name = db.Column(db.String(50), nullable=False, server_default=u'', unique=True)  # for @roles_accepted()


class UserRoles(db.Model):
    __tablename__ = 'user_roles'
    id = db.Column(db.Integer(), primary_key=True)
    user_id = db.Column(db.Integer(), db.ForeignKey('user.id', ondelete='CASCADE'))
    role_id = db.Column(db.Integer(), db.ForeignKey('roles.id', ondelete='CASCADE'))
    

class SurveyModel(db.Model):
    __tablename__ = 'survey'

    id = db.Column(db.Integer, primary_key = True)
    module = db.Column(db.String(55))
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    questions = db.relationship('QuestionModel', backref='survey', lazy='dynamic')

    def to_dict(self):
        return dict(id = self.id,
                    module = self.module,
                    questions = [question.to_dict() for question in self.questions])


class QuestionModel(db.Model):
    __tablename__ = 'questions'

    id = db.Column(db.Integer, primary_key=True)
    label = db.Column(db.String(55), nullable=False)
    survey_id = db.Column(db.Integer, db.ForeignKey('survey.id'))
    answer = db.Column(db.ARRAY(db.String))
    actions = db.relationship('ActionModel', backref='questions', lazy='dynamic')

    def to_dict(self):
        return dict(id = self.id,
                    label = self.label,
                    answer = self.answer,
                    survey_id = self.survey_id,
                    actions = self.actions)

class ActionModel(db.Model):
    __tablename__ = 'actions'

    id = db.Column(db.Integer, primary_key=True)
    label = db.Column(db.String(55), nullable=False)
    question_id = db.Column(db.Integer, db.ForeignKey('questions.id'))
    completed = db.Column(db.Boolean())
    completed_on = db.Column(db.DateTime())

    def to_dict(self):
        return dict(id = self.id,
                    label = self.label,
                    question_id = self.question_id,
                    completed = self.completed,
                    completed_on = self.completed_on)
