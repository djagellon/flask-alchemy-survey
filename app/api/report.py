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
    scores = []
    overall_score = 0
    overall_grade = 'B'

    surveys = [r.to_dict() for r in user.surveys.all()]

    for s in surveys:
        score_data = get_score_for_module(s['module']).json

        scores.append(score_data['score'])

        data.append({
            'module': s.get('module'),
            'started': s.get('started_on'),
            'completed': s.get('completed_on'),
            'score': score_data['score'],
            'grade': score_data['grade']
        })

    pending = [{'module': a} for a in ALL_REPORTS if a not in [s['module'] for s in surveys]]

    if len(scores):
        overall_score = round(sum(scores) / len(scores), 2)
        overall_grade = get_score_grade(overall_score)

    return jsonify({'data': data + pending, 'overall': {'score': overall_score, 'grade': overall_grade}})

@bp.route('/reports/score/<module>/', methods=['GET'])
@token_auth.login_required
def get_score_for_module(module):
    score = 0
    user = get_user()

    survey = user.surveys.filter_by(module=module).first()
    completed = get_completed_actions(module)

    if not survey:
        return

    with open('surveys/outputs.json') as f:
        outputs = json.load(f)

    for question in survey.questions.all():
        answer_list = get_formatted_answers(question)

        for label, checked in answer_list:
            outdata = outputs.get(label, None)

            if not outdata:
                continue

            checked = int(checked)
            output_score = outdata.get('score')

            # Leading '~' will increment score for unchecked answers 
            if output_score and output_score.startswith('~'):
                if not checked:
                    score = score + float(output_score[1:])

            elif output_score and checked:
                score = score + float(output_score)

            # increment completed action scores
            if outdata and outdata.get('actions'):
                for action_label, action in outdata['actions'].items():

                    if action_label in completed:
                        completed.pop(completed.index(action_label))
                        score = score + float(action.get('score', 0))

    grade = get_score_grade(score)

    return jsonify({'score':score, 'grade': grade})

def get_formatted_answers(question):
    """ Return list of format question answers
    Answers should be in typleformat: (label, answer)
    """

    answers = []
    question_answers = question.answer
    question_type = question.question_type

    for answer in question_answers:
        #TODO python 3 can unpack this with "*"
        if question_type == 'MultiField':
            label, checked = answer
        else:
            label, checked = answer, 1

        answers.append((label, checked))

    return answers

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

@bp.route('/reports/answers/<module>/', methods=['GET'])
@token_auth.login_required
def get_answer_for_module(module):

    answers = []
    action_labels = []
    score = 0

    user = get_user()

    survey = user.surveys.filter_by(module=module).first()

    completed_actions = get_completed_actions(module)

    if not survey:
        return

    with open('surveys/outputs.json') as f:
        outputs = json.load(f)

    def check_if_answered(label):
        # Checks if given label was answered

        question_label = label.split('.')[0]
        question = survey.questions.filter_by(label=question_label).first()
        answers = question.answer

        if question.question_type == "MultiField":
            answers = [a[0] for a in answers if int(a[1])]

        return label in answers

    def get_outputs_for_answer(answer_label, checked):
        """ Returns the output and action items based on questions answerd.
        Multiselect question types can have outputs based on unchecked answers.
        """
        outdata = outputs.get(answer_label)

        if not outdata:
            return

        outdata['answer_label'] = label
        actions = outdata.get('actions', {}) or {}

        for action_label, action in actions.items():

            # No output returned if 'not' in action label and answer checked
            if 'not' in action_label.split('.') and int(checked):
                del outdata['actions'][action_label]
                continue

            # No output returned if answer not checked and 'not' not in label 
            if not int(checked) and 'not' not in action_label.split('.'):
                del outdata['actions'][action_label]
                continue

            # if action already exists in output don't include it again
            if action_label in action_labels:
                del outdata['actions'][action_label]
                continue

            # Some actions are based on multiple answers
            if action.get('with'):
                conditions = action.get('with')

                for condition in conditions:
                    # only include action in outdata if all 'with' conditions are met 
                    if not check_if_answered(condition):
                        del outdata['actions'][action_label]
                        break

            # Don't return output data until requested
            if outdata.get('short') or outdata.get('long'):
                outdata['has_why'] = True
                del outdata['short']
                del outdata['long']

            # check if answers have been completed
            action['complete'] = action_label in completed_actions

            # track included actions to prevent duplication
            action_labels.append(action_label)

        return outdata

    for question in survey.questions.all():
        answer_list = get_formatted_answers(question)

        for label, checked in answer_list:
            outdata = get_outputs_for_answer(label, checked)

            answers.append(outdata)

    #sort data by weight
    answers.sort(key=lambda x: float(x.get('weight', 0) if x and x.get('weight') else 0), reverse=True)

    return jsonify({'answers': answers})


def get_completed_actions(module):
    """ Returns list of completed actions for given module
    """

    completed = []
    user = get_user()
    survey = user.surveys.filter_by(module=module).first()

    for question in survey.questions.all():
        actions = question.actions.all()
        completed += [action.label for action in actions if action.completed]

    return completed


def check_action_completeness(module, answer_label, action_label):
    # Determine if action has been marked as complete by the user
    question_label = answer_label.split('.')[0]

    user = get_user()
    survey = user.surveys.filter_by(module=module).first()
    question = survey.questions.filter_by(label=question_label).first()

    try:
        answer = question.actions.filter_by(label=action_label).first()
    except AttributeError:
        return False

    if answer:
        return answer.completed

    return False


def get_answer_label(label):
    # labels can come in with qlabel.answer.action
    # we only care about the qlabel.answer
    return '.'.join(label.split('.')[:2])

@bp.route('/reports/complete/<module>/<answer_label>/<action_label>', methods=['GET', 'POST'])
@token_auth.login_required
def toggle_task(module, answer_label, action_label):
    """ 
    Toggles answers if they exists, marks them complete if it doesn't
    """

    question_label = answer_label.split('.')[0]

    user = get_user()
    survey = user.surveys.filter_by(module=module).first()
    question = survey.questions.filter_by(label=question_label).first()
    action = question.actions.filter_by(label=action_label).first()

    if action:
        action.completed = not action.completed

    else:
        action = ActionModel(
            label=action_label, 
            question_id=question.id, 
            completed=True, 
            completed_on=datetime.now())

    db.session.add(action)
    db.session.commit()

    return jsonify({'success': True, 'complete': action.completed})

@bp.route('/reports/output/<output_type>/<answer_label>/<action_label>', methods=['GET'])
@token_auth.login_required
def get_output(output_type, answer_label, action_label):

    with open('surveys/outputs.json') as f:
        outputs = json.load(f)

    answers = outputs.get(answer_label)
    
    if output_type == 'why':
         output = answers.get('short') or ''
         output += '\n\n' + (answers.get('long') or '')
    else:    
        try:
            output = outputs[answer_label]['actions'][action_label][output_type]
        except TypeError:
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
