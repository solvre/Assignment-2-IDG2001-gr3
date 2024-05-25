from flask import Blueprint, request, jsonify
from app.models import Post
from app import db, redis_client

posts_bp = Blueprint('posts', __name__)

@posts_bp.route('/create_post', methods=['POST'])
def create_post():
    session_token = request.headers.get('Authorization')
    user_id = redis_client.get(session_token)
    if not user_id:
        return jsonify({"error": "Unauthorized"}), 401
    data = request.get_json()
    category = data.get('category')
    text = data.get('text')
    if not category or not text:
        return jsonify({"error": "Missing data"}), 400
    new_post = Post(user_id=user_id, category=category, text=text)
    db.session.add(new_post)
    db.session.commit()
    return jsonify({"message": "Post created successfully"}), 201

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
