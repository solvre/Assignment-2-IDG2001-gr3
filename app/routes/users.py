from flask import Blueprint, jsonify
from app.models import User

users_bp = Blueprint('users', __name__)

@users_bp.route('/user/<int:user_id>', methods=['GET'])
def view_user_profile(user_id):
    user = User.query.get(user_id)
    if not user:
        return jsonify({"error": "User not found"}), 404
    return jsonify({
        "id": user.id,
        "username": user.username,
        "email": user.email,
        "date_created": user.date_created
    })
