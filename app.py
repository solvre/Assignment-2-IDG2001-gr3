from flask import Flask, render_template


app = Flask(__name__)

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/welcome')
def welcome():
    return render_template('welcome.html')

@app.route('/login')
def login():
    return render_template('login.html')

@app.route('/signup')
def signup():
    return render_template('signup.html')

@app.route('/makePost')
def make_post():
    return render_template('makePost.html')

@app.route('/profile')
def profile():
    return render_template('profile.html')

@app.route('/category1')
def category1():
    return render_template('category1.html')

@app.route('/category2')
def category2():
    return render_template('category2.html')

@app.route('/category3')
def category3():
    return render_template('category3.html')

if __name__ == '__main__':
    app.run(debug=True, port=8000)

