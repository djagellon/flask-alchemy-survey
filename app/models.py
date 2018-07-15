from app import db
from datetime import datetime

class SurveyModel(db.Model):
    __tablename__ = 'survey'

    #TODO: link to account details
    id = db.Column(db.Integer, primary_key = True)
    module = db.Column(db.String(55))
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
