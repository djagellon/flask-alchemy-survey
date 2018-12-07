from app import db
from flask import jsonify
from app.models import User, UserPreferences, Preferences, Role, UserRoles
from app.api import bp
from flask_user import current_user, roles_required


@bp.route('/user/',  defaults={'id': None}, methods=['GET'])
@bp.route('/user/<int:id>', methods=['GET'])
def get_user(id=None):

    return jsonify(User.query.get_or_404(id or current_user.id).to_dict())


@bp.route('/username/<string:username>', methods=['GET'])
def get_user_by_username(username):

    if not username:
        return get_user()

    user = User.query.filter_by(username=username).first_or_404()

    return jsonify(user.to_dict())


@bp.route('/user/toggle_pref/<string:pref>', methods=['GET'])
def toggle_preference(pref):
    #specific to admin controls for now

    user = User.query.get_or_404(current_user.id)
    user_preference = user.preferences.filter_by(name=pref).first()


    if user_preference:
        if user_preference.preference == 'on':
            user_preference.preference = 'off'
        else:
            user_preference.preference = 'on'

        db.session.add(user_preference)    

    else:
        pref = Preferences.query.filter_by(name=pref).first_or_404()
        add_pref = UserPreferences(user_id=user.id, preference_id=pref.id)
        db.session.add(add_pref)

    db.session.commit()

    return jsonify({'success': True})


@bp.route('/user/toggle_admin/<string:username>', methods=['GET'])
@roles_required('admin')
def toggle_admin_user(username):

    user = User.query.filter_by(username=username).first_or_404()
    admin_role = Role.query.filter_by(name='admin').first_or_404()

    if not user.is_admin:
        action = UserRoles(user_id=user.id, role_id=admin_role.id) 
        db.session.add(action)    
    else:
        action = UserRoles.query.filter_by(user_id=user.id).filter_by(role_id=admin_role.id).first()
        db.session.delete(action)

    db.session.commit()

    return jsonify({'success': True})

@bp.route('/user/get_access/', methods=['GET'])
def get_access():

    user = get_user()

    return jsonify({
        'admin': 'admin' in user.json['roles']
    })
