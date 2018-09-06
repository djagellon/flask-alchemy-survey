from flask import jsonify
from app.models import User
from app.api import bp
from flask_login import current_user

@bp.route('/report/<int:id>', methods=['GET'])
def get_user(id):
    return User.query.get_or_404(id)
