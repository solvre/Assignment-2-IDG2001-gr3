from flask import Flask, render_template, request, redirect, url_for
from typing import List, Dict
import mysql.connector
import json

app = Flask(__name__)

def get_db_connection():
    config = {
        'user': 'root',            # Default XAMPP MySQL user
        'password': '',            # Default XAMPP MySQL password is usually empty
        'host': 'localhost',       # XAMPP MySQL host
        'port': '3306',            # XAMPP MySQL port
        'database': 'cloudtech' # Database name
    }
    connection = mysql.connector.connect(**config)
    return connection

@app.route('/')
def index() -> str:
    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)
    cursor.execute('SELECT * FROM posts')
    posts = cursor.fetchall()
    cursor.close()
    connection.close()
    return render_template('../Templates/index.html', posts=posts)

@app.route('/post/<int:post_id>')
def post(post_id: int) -> str:
    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)
    cursor.execute('SELECT * FROM posts WHERE id = %s', (post_id,))
    post = cursor.fetchone()
    cursor.execute('SELECT * FROM comments WHERE post_id = %s', (post_id,))
    comments = cursor.fetchall()
    cursor.close()
    connection.close()
    return render_template('../Templates/post.html', post=post, comments=comments)

@app.route('/create_post', methods=['GET', 'POST'])
def create_post():
    if request.method == 'POST':
        title = request.form['title']
        content = request.form['content']
        connection = get_db_connection()
        cursor = connection.cursor()
        cursor.execute('INSERT INTO posts (title, content) VALUES (%s, %s)', (title, content))
        connection.commit()
        cursor.close()
        connection.close()
        return redirect(url_for('index'))
    return render_template('../Templates/create_post.html')

@app.route('/add_comment/<int:post_id>', methods=['POST'])
def add_comment(post_id: int):
    content = request.form['content']
    connection = get_db_connection()
    cursor = connection.cursor()
    cursor.execute('INSERT INTO comments (post_id, content) VALUES (%s, %s)', (post_id, content))
    connection.commit()
    cursor.close()
    connection.close()
    return redirect(url_for('post', post_id=post_id))

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000)
