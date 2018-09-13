from flask import jsonify
from app.models import SurveyModel
from app.api import bp, users
from flask_user import current_user
import json

@bp.route('/report/<module>', methods=['GET'])
def get_answer_for_module(module):

    user = users.get_user(current_user.id)

    survey = user.surveys.filter_by(module=module).first()

    # Solution lookup for each answer
    with open('surveys/asset_output.json') as f:
        outputs = json.load(f)

    answers = []

    for question in survey.questions.all():
        data = question.to_dict()

        try:
            outdata = outputs[data['answer'][0]] 
        except KeyError:
            #TODO Handle open end data
            outdata = outputs[data['label']]

        data['text'] = outdata['question']
        data['output'] = outdata

        answers.append(data)

    return jsonify(answers)
