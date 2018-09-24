from flask import jsonify
from app.models import User
from app.api import bp
from flask_user import current_user


@bp.route('/user/',  defaults={'id': None}, methods=['GET'])
@bp.route('/user/<int:id>', methods=['GET'])
def get_user(id):

    return User.query.get_or_404(id or current_user.id)


@bp.route('/user/has_full_access/', methods=['GET'])
def has_full_access():

    user = get_user()
    return 'admin' in [role.name for role in user.roles]
