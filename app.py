from flask import Flask, render_template, request, redirect, url_for
from models import db, User, Post
from redis import Redis

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://user:password@db/reddit_clone'
db.init_app(app)
redis = Redis(host='redis', port=6379)

@app.route('/')
def index():
    posts = Post.query.limit(10).all()
    return render_template('index.html', posts=posts)

@app.route('/posts', methods=['POST'])
def create_post():
    data = request.form
    new_post = Post(user=data['user'], category=data['category'], text=data['text'])
    db.session.add(new_post)
    db.session.commit()
    return redirect(url_for('index'))

@app.route('/like/<int:post_id>', methods=['POST'])
def like_post(post_id):
    redis.incr(f'post:{post_id}:likes')
    return '', 204

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=80)