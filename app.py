from flask import Flask
from flask import url_for, escape

app = Flask(__name__)

@app.route('/home')
@app.route('/index')
@app.route('/')
def hello():
    return '<h1>Welcome to My Watchlist</h1> <img src="http://helloflask.com/totoro.gif">'

@app.route('/user/<name>')
def user_page(name):
    return 'User: %s' % escape(name)

@app.route('/test')
def test_url_for():
    print(url_for('hello'))
    print(url_for('user_page', name='hanqingqing'))
    print(url_for('test_url_for'))
    print(url_for('test_url_for', user='zhuliuting'))
    return 'Test page'
