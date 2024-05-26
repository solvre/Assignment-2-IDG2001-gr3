from flask import Blueprint, request, jsonify, render_template, session, redirect, url_for, flash
from app.models import Post, User, Category, db, PostLikes
from app import redis_client
from datetime import datetime

posts_bp = Blueprint('posts', __name__)

@posts_bp.route('/')
def index():
    category_id = request.args.get('category_id', type=int)
    if category_id:
        posts = Post.query.filter_by(category_id=category_id).order_by(Post.date.desc()).limit(10).all()
    else:
        posts = Post.query.order_by(Post.date.desc()).limit(10).all()

    categories = Category.query.all()
    return render_template('index.html', posts=posts, categories=categories, selected_category=category_id)


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
        subject = data.get('subject')
        text = data.get('text')
        category_id = data.get('category_id')
        new_category = data.get('new_category')

        if not category_id and not new_category:
            return jsonify({"error": "Category is required"}), 400

        if new_category:
            # Check if the new category already exists
            existing_category = Category.query.filter_by(name=new_category).first()
            if existing_category:
                category_id = existing_category.id
            else:
                # Create new category
                category = Category(name=new_category)
                db.session.add(category)
                db.session.commit()
                category_id = category.id

        if not text or not subject:
            return jsonify({"error": "Missing data"}), 400

        new_post = Post(user_id=int(user_id), category_id=category_id, subject=subject, text=text, date=datetime.utcnow())
        db.session.add(new_post)
        db.session.commit()

        success_message = "Post created successfully"
        categories = Category.query.all()
        return render_template('create_post.html', success_message=success_message, categories=categories)

    categories = Category.query.all()
    return render_template('create_post.html', categories=categories)

@posts_bp.route('/user_posts/<int:user_id>', methods=['GET'])
def view_user_posts(user_id):
    user = User.query.get(user_id)
    if not user:
        return jsonify({"error": "User not found"}), 404
    
    posts = Post.query.filter_by(user_id=user_id).order_by(Post.date.desc()).all()
    return render_template('user_posts.html', user=user, posts=posts)


@posts_bp.route('/like_post/<int:post_id>', methods=['POST'])
def like_post(post_id):
    if 'session_token' not in session or not session['session_token']:
        return redirect(url_for('auth.login', next=request.url))

    session_token = session.get('session_token')
    user_id = redis_client.get(session_token)

    if not user_id:
        flash("Unauthorized access", "error")
        return redirect(url_for('auth.login'))

    post = Post.query.get(post_id)
    if not post:
        flash("Post not found", "error")
        return redirect(url_for('posts.index'))

    existing_like = PostLikes.query.filter_by(post_id=post_id, user_id=int(user_id)).first()
    if existing_like:
        if existing_like.like_type == 1:
            db.session.delete(existing_like)
            post.likes -= 1
        else:
            existing_like.like_type = 1
            post.likes += 2
    else:
        new_like = PostLikes(post_id=post_id, user_id=int(user_id), like_type=1)
        db.session.add(new_like)
        post.likes += 1

    db.session.commit()
    return redirect(url_for('posts.index'))

@posts_bp.route('/dislike_post/<int:post_id>', methods=['POST'])
def dislike_post(post_id):
    if 'session_token' not in session or not session['session_token']:
        return redirect(url_for('auth.login', next=request.url))

    session_token = session.get('session_token')
    user_id = redis_client.get(session_token)

    if not user_id:
        flash("Unauthorized access", "error")
        return redirect(url_for('auth.login'))

    post = Post.query.get(post_id)
    if not post:
        flash("Post not found", "error")
        return redirect(url_for('posts.index'))

    existing_like = PostLikes.query.filter_by(post_id=post_id, user_id=int(user_id)).first()
    if existing_like:
        if existing_like.like_type == -1:
            db.session.delete(existing_like)
            post.likes += 1
        else:
            existing_like.like_type = -1
            post.likes -= 2
    else:
        new_dislike = PostLikes(post_id=post_id, user_id=int(user_id), like_type=-1)
        db.session.add(new_dislike)
        post.likes -= 1

    db.session.commit()
    return redirect(url_for('posts.index'))

@posts_bp.route('/delete_post/<int:post_id>', methods=['POST'])
def delete_post(post_id):
    if 'session_token' not in session or not session['session_token']:
        flash("Unauthorized access", "error")
        return redirect(url_for('auth.login'))

    session_token = session.get('session_token')
    user_id = redis_client.get(session_token)

    if not user_id:
        flash("Unauthorized access", "error")
        return redirect(url_for('auth.login'))

    post = Post.query.get(post_id)
    if not post:
        flash("Post not found", "error")
        return redirect(url_for('posts.index'))

    if post.user_id != int(user_id):
        flash("Unauthorized access", "error")
        return redirect(url_for('posts.index'))

    PostLikes.query.filter_by(post_id=post_id).delete()
    db.session.delete(post)
    db.session.commit()

    flash("Post deleted successfully", "success")
    return redirect(url_for('posts.index'))
