from app import db
from datetime import datetime

class User(db.Model):
    __tablename__ = 'user'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), index=True, unique=True)
    email = db.Column(db.String(120), index=True, unique=True)
    password_hash = db.Column(db.String(128))
    admin = db.Column(db.Boolean)
    surveys = db.relationship('SurveyModel', backref='user', lazy=False)

    def __repr__(self):
        return '<User {}>'.format(self.username)

class SurveyModel(db.Model):
    __tablename__ = 'survey'

    #TODO: link to account details
    id = db.Column(db.Integer, primary_key = True)
    module = db.Column(db.String(55))
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    questions = db.relationship('QuestionModel', backref='survey', lazy=False)

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
