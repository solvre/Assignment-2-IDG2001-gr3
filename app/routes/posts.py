from flask import Blueprint, request, jsonify, render_template, session, redirect, url_for
from app.models import Post
from app import db, redis_client
from datetime import datetime

posts_bp = Blueprint('posts', __name__)

# Route to render the home page with the latest posts
@posts_bp.route('/')
def index():
    posts = Post.query.order_by(Post.date.desc()).limit(10).all()
    return render_template('index.html', posts=posts)

# Route to create a new post
@posts_bp.route('/create_post', methods=['GET', 'POST'])
def create_post():
    if request.method == 'POST':
        # Retrieve the session token from the session
        session_token = session.get('session_token')
        print(f"Session token: {session_token}")

        # Check if the session token is None and handle it
        if not session_token:
            return jsonify({"error": "Unauthorized"}), 401

        user_id = redis_client.get(session_token)
        print(f"User ID from Redis: {user_id}")

        if not user_id:
            return jsonify({"error": "Unauthorized"}), 401

        data = request.form
        category = data.get('category')
        text = data.get('text')
        print(f"Category: {category}, Text: {text}")

        if not category or not text:
            return jsonify({"error": "Missing data"}), 400

        new_post = Post(user_id=int(user_id), category=category, text=text, date=datetime.utcnow())
        db.session.add(new_post)
        db.session.commit()

        print("Post created successfully")
        return jsonify({"message": "Post created successfully"}), 201

    return render_template('create_post.html')
