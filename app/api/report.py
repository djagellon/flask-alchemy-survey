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

        answers.append(outdata)

    #sort data by weight
    answers.sort(key=lambda x: int(x['weight'] or 0), reverse=True)
    return jsonify(answers)


def get_answer_label(label):
    # labels can come in with qlabel.answer.action
    # we only care about the qlabel.answer
    return '.'.join(label.split('.')[:2])

@bp.route('/report/<type>/<module>/<label>', methods=['GET'])
def get_output(type, module, label):

    label = get_answer_label(label)

    with open('surveys/%s_output.json' % module) as f:
        outputs = json.load(f)

    try:
        output = outputs[label][type]
    except KeyError:
        print "NO OUTPUT FOUND FOR %s" % label
        output = 'No further information available'

    return jsonify(output)

