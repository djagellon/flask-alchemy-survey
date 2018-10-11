from app import db
from flask import jsonify
from app.models import User, UserPreferences, Preferences
from app.api import bp
from flask_user import current_user


@bp.route('/user/',  defaults={'id': None}, methods=['GET'])
@bp.route('/user/<int:id>', methods=['GET'])
def get_user(id=None):

    return jsonify(User.query.get_or_404(id or current_user.id).to_dict())


@bp.route('/user/toggle_pref/<pref>', methods=['GET'])
def toggle_preference(pref):
    #specific to admin controls for now

    user = User.query.get_or_404(current_user.id)
    user_preference = user.preferences.filter_by(name=pref).first()

    if not user_preference:
        return jsonify({'success': False})

    if user_preference.preference == 'on':
        user_preference.preference = 'off'
    else:
        user_preference.preference = 'on'

    db.session.add(user_preference)    
    db.session.commit()

    return jsonify({'success': True})


@bp.route('/user/get_access/', methods=['GET'])
def get_access():

    user = get_user()

    return jsonify({
        'admin': 'admin' in user.json['roles']
    })
