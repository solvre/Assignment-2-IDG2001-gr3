from flask import Blueprint, request, jsonify, render_template, session, redirect, url_for
from app.models import Post
from app import db, redis_client
from datetime import datetime

posts_bp = Blueprint('posts', __name__)

# Route to render the home page with the latest posts
@posts_bp.route('/')
def index():
    category = request.args.get('category', None)
    if category:
        posts = Post.query.filter_by(category=category).order_by(Post.date.desc()).limit(10).all()
    else:
        posts = Post.query.order_by(Post.date.desc()).limit(10).all()
    return render_template('index.html', posts=posts, selected_category=category)

# Route to create a new post
@posts_bp.route('/create_post', methods=['GET', 'POST'])
def create_post():
    if 'session_token' not in session or not session['session_token']:
        return redirect(url_for('auth.login', next=request.url))

    if request.method == 'POST':
        session_token = session.get('session_token')
        user_id = redis_client.get(session_token)

        if not user_id:
            return jsonify({"error": "Unauthorized"}), 401

        data = request.form
        category = data.get('category')
        text = data.get('text')

        if not category or not text:
            return jsonify({"error": "Missing data"}), 400

        new_post = Post(user_id=int(user_id), category=category, text=text, date=datetime.utcnow())
        db.session.add(new_post)
        db.session.commit()

        success_message = "Post created successfully"
        return render_template('create_post.html', success_message=success_message)

    return render_template('create_post.html')
