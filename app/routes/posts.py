from flask import Blueprint, request, jsonify, render_template
from app.models import Post, User
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
        session_token = request.headers.get('Authorization')
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
        return jsonify({"message": "Post created successfully"}), 201
    return render_template('create_post.html')

# Route to view posts by category
@posts_bp.route('/posts/<category>', methods=['GET'])
def view_posts_by_category(category):
    posts = Post.query.filter_by(category=category).order_by(Post.date.desc()).limit(10).all()
    return jsonify([{
        "id": post.id,
        "user_id": post.user_id,
        "category": post.category,
        "text": post.text,
        "date": post.date,
        "likes": post.likes
    } for post in posts])

# Route to view posts by a specific user
@posts_bp.route('/user_posts/<int:user_id>', methods=['GET'])
def view_posts_by_user(user_id):
    posts = Post.query.filter_by(user_id=user_id).order_by(Post.date.desc()).all()
    return jsonify([{
        "id": post.id,
        "user_id": post.user_id,
        "category": post.category,
        "text": post.text,
        "date": post.date,
        "likes": post.likes
    } for post in posts])

# Route to like a post
@posts_bp.route('/like_post/<int:post_id>', methods=['POST'])
def like_post(post_id):
    session_token = request.headers.get('Authorization')
    user_id = redis_client.get(session_token)
    if not user_id:
        return jsonify({"error": "Unauthorized"}), 401
    post = Post.query.get(post_id)
    if not post:
        return jsonify({"error": "Post not found"}), 404
    redis_client.incr(f'post:{post_id}:likes')
    return jsonify({"message": "Post liked successfully"}), 200

# Route to view a specific post
@posts_bp.route('/post/<int:post_id>', methods=['GET'])
def view_post(post_id):
    post = Post.query.get(post_id)
    if not post:
        return jsonify({"error": "Post not found"}), 404
    return jsonify({
        "id": post.id,
        "user_id": post.user_id,
        "category": post.category,
        "text": post.text,
        "date": post.date,
        "likes": post.likes
    })

# Route to delete a post
@posts_bp.route('/delete_post/<int:post_id>', methods=['DELETE'])
def delete_post(post_id):
    session_token = request.headers.get('Authorization')
    user_id = redis_client.get(session_token)
    if not user_id:
        return jsonify({"error": "Unauthorized"}), 401
    post = Post.query.get(post_id)
    if not post:
        return jsonify({"error": "Post not found"}), 404
    if post.user_id != int(user_id):
        return jsonify({"error": "Unauthorized"}), 401
    db.session.delete(post)
    db.session.commit()
    return jsonify({"message": "Post deleted successfully"}), 200
