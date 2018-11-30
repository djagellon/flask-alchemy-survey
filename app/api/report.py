from app import db
from flask import jsonify, url_for
from flask import g
from app.models import User, SurveyModel, QuestionModel, ActionModel
from app.api import bp
from app.api.auth import token_auth
from flask_user import current_user, roles_required
import json
from datetime import datetime

ALL_REPORTS = ["asset", "governance", "risk", "remediation"]

def get_user():

    user = getattr(g, 'current_user', current_user)

    return User.query.get_or_404(user.id)

@bp.route('/reports/canstart/<module>')
@token_auth.login_required
def can_start(module):
    # A module can only be taken if the previous module is completed
    user = get_user()

    try:
        module_index = ALL_REPORTS.index(module)
    except ValueError:
        #Allow test modules
        return True

    if module_index == 0:
        return True

    prev_module = ALL_REPORTS[module_index - 1]
    prev_survey = user.surveys.filter_by(module=prev_module).first()

    return prev_survey and prev_survey.completed_on

@bp.route('/reports/user/', defaults={'user_id': None}, methods=['GET'])
@token_auth.login_required
def get_user_reports(user_id=None):

    user = get_user()
    data = []

    surveys = [r.to_dict() for r in user.surveys.all()]

    for s in surveys:
        score_data = get_score_for_module(s['module']).json

        data.append({
            'module': s.get('module'),
            'started': s.get('started_on'),
            'completed': s.get('completed_on'),
            'score': score_data['score'],
            'grade': score_data['grade']
        })

    pending = [{'module': a} for a in ALL_REPORTS if a not in [s['module'] for s in surveys]]

    return jsonify(data + pending)

@bp.route('/reports/score/<module>/', methods=['GET'])
@token_auth.login_required
def get_score_for_module(module):
    score = 0
    user = get_user()

    survey = user.surveys.filter_by(module=module).first()

    with open('surveys/outputs.json') as f:
        outputs = json.load(f)

    if survey and survey.questions:

        for question in survey.questions.all():
            data = question.to_dict()

            question_answers = data['answer']

            for answer in question_answers:
                outdata = outputs.get(answer, outputs.get(data['label'], None))

                if outdata and outdata.get('score'):
                    score = score + float(outdata['score'])

    grade = get_score_grade(score)

    return jsonify({'score':score, 'grade': grade})

def get_score_grade(score):
    if score < 60:
        return 'F'
    elif 60 <= score < 70:
        return 'D'
    elif 70 <= score < 80:
        return 'C'
    elif 80 <= score < 90:
        return 'B'
    else:
        return 'A'

@bp.route('/reports/<module>/', methods=['GET'])
@token_auth.login_required
def get_answer_for_module(module):

    answers = []
    score = 0

    user = get_user()

    survey = user.surveys.filter_by(module=module).first()

    with open('surveys/outputs.json') as f:
        outputs = json.load(f)

    def get_outputs_for_answer(answer):
        outdata = outputs.get(answer, outputs.get(data['label'], None))

        if not outdata:
            return

        # check if answers have been completed
        if outdata['actions']:
            for action in outdata['actions']:
                complete = check_action_completeness(module, action)
                outdata['actions'][action]['complete'] = complete

        # Don't return output data until requested
        if outdata.get('short') or outdata.get('long'):
            outdata['has_why'] = True
            del outdata['short']
            del outdata['long']

        return outdata

    if survey and survey.questions:
        # Solution lookup for each answer

        for question in survey.questions.all():
            data = question.to_dict()

            question_answers = data['answer']

            for answer in question_answers:
                outdata = get_outputs_for_answer(answer)

                if outdata and outdata.get('score'):
                    score = score + float(outdata['score'])

                answers.append(outdata)

    #sort data by weight
    answers.sort(key=lambda x: int(x.get('weight', 0) if x and x.get('weight') else 0), reverse=True)

    return jsonify({'answers': answers, 'score':score})


def check_action_completeness(module, action):
    # Determine if action has been marked as complete by the user
    action_split = action.split('.')
    q_label = action_split[0]
    q_answer = '.'.join(action_split[:-1])

    user = get_user()
    survey = user.surveys.filter_by(module=module).first()
    question = survey.questions.filter_by(label=q_label).first()

    if question:
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

@bp.route('/reports/<output_type>/<action_label>', methods=['GET'])
@token_auth.login_required
def get_output(output_type, action_label):

    answer_label = get_answer_label(action_label)

    with open('surveys/outputs.json') as f:
        outputs = json.load(f)

    answers = outputs.get(answer_label)

    if output_type == 'why':
        output = answers.get('short') or ''
        output += '\n\n' + (answers.get('long') or '')
    else:    
        try:
            output = answers['actions'][action_label][output_type]
        except KeyError:
            print "NO %s OUTPUT FOUND FOR %s" % (output_type, action_label)
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
