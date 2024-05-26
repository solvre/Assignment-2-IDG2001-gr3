from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
import redis
import os
from datetime import datetime

app = Flask(__name__)

# Configure the SQLAlchemy part of the app instance
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:@localhost/cloud'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Create the SQLAlchemy db instance
db = SQLAlchemy(app)

# Initialize Redis
redis_host = 'redis-19735.c327.europe-west1-2.gce.redns.redis-cloud.com'  # Replace with your Redis host from Redis Labs
redis_port = 19735  # Replace with your Redis port from Redis Labs
redis_password = 'kJchBWfmn3lc319JRFjWxGGMrX6ef6ib'  # Replace with your Redis password
redis_client = redis.StrictRedis(host=redis_host, port=redis_port, password=redis_password, db=0)

# Define models
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    date_created = db.Column(db.DateTime, default=datetime.utcnow)

class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    category = db.Column(db.String(80), nullable=False)
    text = db.Column(db.Text, nullable=False)
    date = db.Column(db.DateTime, default=datetime.utcnow)
    likes = db.Column(db.Integer, default=0)

@app.route('/')
def index():
    return "Hello, World!"

@app.route('/test_db')
def test_db():
    try:
        # Attempt to query the User table
        user_count = User.query.count()
        return jsonify({"message": f"Database connected successfully. User count: {user_count}"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/test_redis')
def test_redis():
    try:
        # Attempt to set and get a value in Redis
        redis_client.set('test', 'Redis is connected')
        value = redis_client.get('test').decode('utf-8')
        return jsonify({"message": f"{value}"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Additional routes and functionalities go here

if __name__ == '__main__':
    print("Starting Flask app")
    app = create_app()
    app.run(host='0.0.0.0', port=5000, debug=True)