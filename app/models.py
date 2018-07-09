from app import db

class SurveyModel(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    q1 = db.Column(db.String(20))
    q2 = db.Column(db.String(20))
    q2a = db.Column(db.String(255))
    q2b = db.Column(db.String(255))

    # def __init__(self, q1=None, q2=None):
    #     self.q1 = q1
    #     self.q2 = q2
        # self.q2a = q2a
        # self.q2b = q2b

