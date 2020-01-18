from flask import Flask, render_template
from flask import url_for, escape

app = Flask(__name__)

name = 'hanqingqing'
movies = [
    {'title': 'My macos', 'year': '2018'},
    {'title': 'My windows', 'year': '2013'},
    {'title': 'My ubuntu', 'year': '2018'},
]

@app.route('/home')
@app.route('/index')
@app.route('/hello')
def hello():
    return '<h1>Welcome to My Watchlist</h1> <img src="http://helloflask.com/totoro.gif">'

@app.route('/user/<name>')
def user_page(name):
    return 'User: %s' % escape(name)

@app.route('/')
def index():
    return render_template('index.html', name=name, movies=movies)

@app.route('/test')
def test_url_for():
    print(url_for('hello'))
    print(url_for('user_page', name='hanqingqing'))
    print(url_for('test_url_for'))
    print(url_for('test_url_for', user='zhuliuting'))
    return 'Test page'
