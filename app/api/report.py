from app import db
from flask import jsonify, url_for
from app.models import User, SurveyModel, QuestionModel, ActionModel
from app.api import bp
from flask_user import current_user
import json
from datetime import datetime

ALL_REPORTS = set(["asset", "governance", "risk", "remediation"])

def get_user():
    return User.query.get_or_404(current_user.id)

@bp.route('/reports/user/', defaults={'user_id': None}, methods=['GET'])
@bp.route('/reports/user/<user_id>/', methods=['GET'])
def get_user_reports(user_id=None):

    user = get_user()

    completed = [r.module for r in user.surveys.all() if r.completed_on] 
    pending = ALL_REPORTS - set(completed)

    return jsonify({'complete': completed, 'pending': list(pending)})

@bp.route('/reports/<module>/', methods=['GET'])
def get_answer_for_module(module):

    answers = []

    user = get_user()

    survey = user.surveys.filter_by(module=module).first()

    if survey and survey.questions:
        # Solution lookup for each answer
        with open('surveys/asset_output.json') as f:
            outputs = json.load(f)


        for question in survey.questions.all():
            data = question.to_dict()

            outdata = outputs[data['answer'][0]] 

            # check if answers have been completed
            for action in outdata['actions']:
                outdata['actions'][action] = {
                    'text': outdata['actions'][action],
                    'complete': check_action_completeness(module, action),
                    'action_url': url_for('api.complete_task', module=module, answer=action) 
                }

            answers.append(outdata)

    #sort data by weight
    answers.sort(key=lambda x: int(x['weight'] or 0), reverse=True)

    return jsonify(answers)

def check_action_completeness(module, action):
    # Determine if action has been marked as complete by the user
    action_split = action.split('.')
    q_label = action_split[0]
    q_answer = '.'.join(action_split[:-1])

    user = get_user()
    survey = user.surveys.filter_by(module=module).first()
    question = survey.questions.filter_by(label=q_label).first()
    answer = question.actions.filter_by(label=action).first()

    if answer:
        return answer.completed

    return False


def get_answer_label(label):
    # labels can come in with qlabel.answer.action
    # we only care about the qlabel.answer
    return '.'.join(label.split('.')[:2])

@bp.route('/reports/complete/<module>/<answer>', methods=['GET', 'POST'])
def complete_task(module, answer):
    ### Mark an answer as completed ###

    ans_split = answer.split('.')
    q_label = ans_split[0]

    user = get_user()
    survey = user.surveys.filter_by(module=module).first()
    question = survey.questions.filter_by(label=q_label).first()

    # TODO: Check for existing action
    action = ActionModel(
        label=answer, 
        question_id=question.id, 
        completed=True, 
        completed_on=datetime.now())

    db.session.add(action)
    db.session.commit()

    return jsonify({'success': True})

@bp.route('/reports/<type>/<module>/<label>', methods=['GET'])
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

@bp.route('/admin/report/all')
def admin_all_reports():
    data = [s.to_dict() for s in SurveyModel.query.all() or []]

    return jsonify(data)