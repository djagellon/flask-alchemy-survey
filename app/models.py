import base64
import os
from flask import current_app 
from app import db
from datetime import datetime, timedelta
from werkzeug.security import generate_password_hash, check_password_hash
from flask_user import UserMixin, TokenManager, PasswordManager


class User(db.Model, UserMixin):
    __tablename__ = 'user'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), index=True, unique=True)
    email = db.Column(db.Unicode(255), index=True, unique=True)
    # email_confirmed_at = db.Column(db.DateTime())

    password = db.Column(db.String(255), nullable=False, server_default='')
    active = db.Column(db.Boolean(), server_default='0')

    surveys = db.relationship('SurveyModel', backref='user', lazy='dynamic')
    preferences = db.relationship('Preferences', secondary='user_preferences', backref='user', lazy='dynamic')
    roles = db.relationship('Role', secondary='user_roles', backref=db.backref('user', lazy='dynamic'))

    token = db.Column(db.String(32), index=True, unique=True)
    token_expiration = db.Column(db.DateTime)

    def __repr__(self):
        return '<User {}>'.format(self.username)

    def to_dict(self):
        return dict(id = self.id,
                    username = self.username,
                    email = self.email,
                    roles = [role.name for role in self.roles],
                    preferences = {p.name: p.preference for p in self.preferences})

    def check_password(self, password):
        return current_app.user_manager.verify_password(password, self.password)

    def get_token(self, expires_in=3600):
        now = datetime.utcnow()

        if self.token and self.token_expiration > now + timedelta(seconds=60):
            return self.token

        self.token = base64.b64encode(os.urandom(24)).decode('utf-8')
        self.token_expiration = now + timedelta(seconds=expires_in)

        db.session.add(self)

        return self.token

    def revoke_token(self):
        self.token_expiration = datetime.utcnow() - timedelta(seconds=1)

    @staticmethod
    def check_token(token):
        user = User.query.filter_by(token=token).first()

        if user is None or user.token_expiration < datetime.utcnow():
            return None

        return user

    def get_preference(self, pref):
        prefs = {p.name: p.preference for p in self.preferences}

        return prefs.get(pref, None)

    @property
    def admin_controls_on(self):
        return self.get_preference('admin_controls') == 'on'

    @property
    def is_admin(self):
        return 'admin' in [role.name for role in self.roles]


class Role(db.Model):
    __tablename__ = 'roles'
    id = db.Column(db.Integer(), primary_key=True)
    name = db.Column(db.String(50), nullable=False, server_default=u'', unique=True)  # for @roles_accepted()


class UserRoles(db.Model):
    __tablename__ = 'user_roles'
    id = db.Column(db.Integer(), primary_key=True)
    user_id = db.Column(db.Integer(), db.ForeignKey('user.id', ondelete='CASCADE'))
    role_id = db.Column(db.Integer(), db.ForeignKey('roles.id', ondelete='CASCADE'))
    

class Preferences(db.Model):
    __tablename__ = 'preferences'
    id = db.Column(db.Integer(), primary_key=True)
    name = db.Column(db.String(50), nullable=False, server_default=u'', unique=True)  
    preference = db.Column(db.String())


class UserPreferences(db.Model):
    __tablename__ = 'user_preferences'
    id = db.Column(db.Integer(), primary_key=True)
    user_id = db.Column(db.Integer(), db.ForeignKey('user.id', ondelete='CASCADE'))
    preference_id = db.Column(db.Integer(), db.ForeignKey('preferences.id', ondelete='CASCADE'))


class SurveyModel(db.Model):
    __tablename__ = 'survey'

    id = db.Column(db.Integer, primary_key = True)
    module = db.Column(db.String(55))
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    questions = db.relationship('QuestionModel', backref='survey', lazy='dynamic')
    started_on = db.Column(db.DateTime())
    completed_on = db.Column(db.DateTime())

    def to_dict(self):
        questions = [question.to_dict() for question in self.questions]
        questions.sort(key=lambda x: x['label'])

        return dict(id = self.id,
                    module = self.module,
                    user = self.user_id,
                    questions = questions,
                    started_on = self.started_on,
                    completed_on = self.completed_on)

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
                    actions = [action.to_dict() for action in self.actions])

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
