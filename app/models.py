from app import db, login
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin

class User(UserMixin, db.Model):
    __tablename__ = 'user'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), index=True, unique=True)
    email = db.Column(db.String(120), index=True, unique=True)
    password_hash = db.Column(db.String(128))
    admin = db.Column(db.Boolean)
    surveys = db.relationship('SurveyModel', backref='user', lazy='dynamic')

    def __repr__(self):
        return '<User {}>'.format(self.username)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

class SurveyModel(db.Model):
    __tablename__ = 'survey'

    #TODO: link to account details
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

    id = db.Column(db.Integer, primary_key = True)
    label = db.Column(db.String(55), nullable=False)
    survey_id = db.Column(db.Integer, db.ForeignKey('survey.id'))
    answer = db.Column(db.ARRAY(db.String))

    def to_dict(self):
        return dict(id = self.id,
                    label = self.label,
                    answer = self.answer,
                    survey_id = self.survey_id)

@login.user_loader
def load_user(id):
    return User.query.get(int(id))