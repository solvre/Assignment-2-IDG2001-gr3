from flask import Blueprint, request, jsonify, render_template
from werkzeug.security import generate_password_hash, check_password_hash
from app.models import User
from app import db, redis_client
import os

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        data = request.form
        username = data.get('username')
        email = data.get('email')
        password = data.get('password')
        if not username or not email or not password:
            return jsonify({"error": "Missing data"}), 400
        hashed_password = generate_password_hash(password)
        new_user = User(username=username, email=email, password=hashed_password)
        db.session.add(new_user)
        db.session.commit()
        return jsonify({"message": "User created successfully"}), 201
    return render_template('register.html')

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        data = request.form
        email = data.get('email')
        password = data.get('password')
        if not email or not password:
            return jsonify({"error": "Missing data"}), 400
        user = User.query.filter_by(email=email).first()
        if user and check_password_hash(user.password, password):
            session_token = os.urandom(24).hex()
            redis_client.set(session_token, user.id)
            return jsonify({"message": "Login successful", "session_token": session_token}), 200
        return jsonify({"error": "Invalid credentials"}), 401
    return render_template('login.html')
