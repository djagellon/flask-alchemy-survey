from app import db
from flask import jsonify, url_for
from flask import g
from app.models import User, SurveyModel, QuestionModel, ActionModel
from app.api import bp
from app.api.auth import token_auth
from flask_user import current_user, roles_required
import json
from datetime import datetime

ALL_REPORTS = set(["asset", "governance", "risk", "remediation"])

def get_user():

    user = getattr(g, 'current_user', current_user)

    return User.query.get_or_404(user.id)

@bp.route('/reports/user/', defaults={'user_id': None}, methods=['GET'])
@token_auth.login_required
def get_user_reports(user_id=None):

    user = get_user()

    completed = [r.module for r in user.surveys.all() if r.completed_on] 
    pending = ALL_REPORTS - set(completed)

    return jsonify({'complete': completed, 'pending': list(pending)})

@bp.route('/reports/<module>/', methods=['GET'])
@token_auth.login_required
def get_answer_for_module(module):

    answers = []

    user = get_user()

    survey = user.surveys.filter_by(module=module).first()

    with open('surveys/outputs.json') as f:
        outputs = json.load(f)

    def get_outputs_for_answer(answer):
        outdata = outputs.get(answer, outputs.get(data['label'], None))

        # check if answers have been completed
        if outdata:
            for action in outdata['actions']:
                complete = check_action_completeness(module, action)
                outdata['actions'][action]['complete'] = complete

        return outdata

    if survey and survey.questions:
        # Solution lookup for each answer

        for question in survey.questions.all():
            data = question.to_dict()

            question_answers = data['answer']

            for answer in question_answers:
                outdata = get_outputs_for_answer(answer)
                answers.append(outdata)

    #sort data by weight
    answers.sort(key=lambda x: int(x.get('weight', 0)), reverse=True)

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
@token_auth.login_required
def toggle_task(module, answer):
    """ 
    Toggles answers if they exists, marks them complete if it doesn't
    """

    ans_split = answer.split('.')
    q_label = ans_split[0]

    user = get_user()
    survey = user.surveys.filter_by(module=module).first()
    question = survey.questions.filter_by(label=q_label).first()
    action = question.actions.filter_by(label=answer).first()

    if action:
        action.completed = not action.completed

    else:
        action = ActionModel(
            label=answer, 
            question_id=question.id, 
            completed=True, 
            completed_on=datetime.now())

    db.session.add(action)
    db.session.commit()

    return jsonify({'success': True, 'complete': action.completed})

@bp.route('/reports/<type>/<module>/<label>', methods=['GET'])
@token_auth.login_required
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
@token_auth.login_required
@roles_required('admin')
def admin_all_reports():
    data = [s.to_dict() for s in SurveyModel.query.all() or []]

    return jsonify(data)

@bp.route('/admin/delete/<module>')
@token_auth.login_required
@roles_required('admin')
def delete_survey(module=None):

    user = get_user()
    
    if module:
        data = user.surveys.filter_by(module=module).all()
    else:
        data = user.surveys.all() 

    for s in data:
        db.session.delete(s)

    db.session.commit()
    return jsonify({'success': True})
