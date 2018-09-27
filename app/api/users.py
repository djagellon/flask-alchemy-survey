from flask import jsonify
from app.models import User
from app.api import bp
from flask_user import current_user


@bp.route('/user/',  defaults={'id': None}, methods=['GET'])
@bp.route('/user/<int:id>', methods=['GET'])
def get_user(id=None):

    return jsonify(User.query.get_or_404(id or current_user.id).to_dict())


@bp.route('/user/has_full_access/', methods=['GET'])
def has_full_access():

    user = get_user()

    return jsonify({
        'has': 'admin' in user.json['roles']
    })
