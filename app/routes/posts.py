from flask import Blueprint, request, jsonify, render_template, session, redirect, url_for, flash
from app.models import Post, User, Category, db, PostLikes
from app import redis_client
from datetime import datetime

posts_bp = Blueprint('posts', __name__)

@posts_bp.route('/')
def index():
    category_id = request.args.get('category_id')
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
            flash("Unauthorized access", "error")
            return redirect(url_for('auth.login'))

        data = request.form
        category_id = data.get('category')
        new_category = data.get('new_category')
        subject = data.get('subject')
        text = data.get('text')

        if not category_id and not new_category:
            flash("Category is required", "error")
            return redirect(url_for('posts.create_post'))

        if not text or not subject:
            flash("Subject and text are required", "error")
            return redirect(url_for('posts.create_post'))

        if new_category:
            category = Category.query.filter_by(name=new_category).first()
            if not category:
                category = Category(name=new_category)
                db.session.add(category)
                db.session.commit()
            category_id = category.id
        else:
            category_id = int(category_id)

        new_post = Post(user_id=int(user_id), category_id=category_id, subject=subject, text=text, date=datetime.utcnow())
        db.session.add(new_post)
        db.session.commit()

        flash("Post created successfully", "success")
        return redirect(url_for('posts.index'))

    categories = Category.query.all()
    return render_template('create_post.html', categories=categories)

@posts_bp.route('/user/<int:user_id>')
def view_user_posts(user_id):
    user = User.query.get(user_id)
    if not user:
        flash("User not found", "error")
        return redirect(url_for('posts.index'))
    posts = Post.query.filter_by(user_id=user_id).order_by(Post.date.desc()).all()
    return render_template('user_posts.html', posts=posts, user=user)

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
