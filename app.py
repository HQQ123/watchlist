# -*- coding:utf-8 -*-
import os
import sys

import click
from flask import Flask, render_template
from flask import url_for, escape
from flask_sqlalchemy import SQLAlchemy

WIN = sys.platform.startswith('win')
if WIN:  # 如果是 Windows 系统，使用三个斜线
    prefix = 'sqlite:///'
else:  # 否则使用四个斜线
    prefix = 'sqlite:////'

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = prefix + os.path.join(app.root_path, 'data.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False  # 关闭对模型修改的监控
db = SQLAlchemy(app)


class User(db.Model):
    """表名自动生成，为user, id与name分别为主键名与列名"""
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(20))


class Movie(db.Model):
    """表名自动生成, 为movie, id与title, year分别为主键名与列名"""
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(60))
    year = db.Column(db.String(4))


@app.cli.command()  # 注册为命令
@click.option('--drop', is_flag=True, help='Create after drop.')  # 设置选项
def initdb(drop):
    """初始化数据库"""
    if drop:
        db.drop_all()
    db.create_all()
    click.echo('Initialized database.')  # 输出提示信息


@app.cli.command()
def forge():
    """生成构造数据"""
    db.create_all()
    name = 'hanqingqing'
    movies = [
        {'title': 'My macos', 'year': '2018'},
        {'title': 'My windows', 'year': '2013'},
        {'title': 'My ubuntu', 'year': '2018'},
    ]
    user = User(name=name)
    db.session.add(user)
    for m in movies:
        movie = Movie(title=m['title'], year=m['year'])
        db.session.add(movie)
    db.session.commit()
    click.echo('Done')


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
    user = User.query.get(2)
    movies = Movie.query.all() 
    return render_template('index.html', user=user, movies=movies)


@app.route('/test')
def test_url_for():
    print(url_for('hello'))
    print(url_for('user_page', name='hanqingqing'))
    print(url_for('test_url_for'))
    print(url_for('test_url_for', user='zhuliuting'))
    return 'Test page'
