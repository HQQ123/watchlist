# -*- coding:utf-8 -*-
import os
import sys

import click
from flask import Flask, render_template
from flask import url_for, escape, request, redirect, flash
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash

WIN = sys.platform.startswith('win')
if WIN:  # 如果是 Windows 系统，使用三个斜线
    prefix = 'sqlite:///'
else:  # 否则使用四个斜线
    prefix = 'sqlite:////'

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = prefix + os.path.join(app.root_path, 'data.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False  # 关闭对模型修改的监控
app.config['SECRET_KEY'] = 'dev'  # 等同于app.secret_key = 'dev'
db = SQLAlchemy(app)

login_manager = LoginManager(app)
login_manager.login_view = 'login'


class User(db.Model, UserMixin):
    """表名自动生成，为user, id与name分别为主键名与列名"""
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(20))
    username = db.Column(db.String(20))  # 用户名
    password_hash = db.Column(db.String(128))  # 密码hash值

    def set_password(self, password):
        """生成密码散列值，参数为密码"""
        self.password_hash = generate_password_hash(password)

    def validate_password(self, password):
        """验证密码, 密码为参数"""
        return check_password_hash(self.password_hash, password)


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


@app.cli.command()
@click.option('--username', prompt=True, help='The username used to login.')
@click.option('--password', prompt=True, hide_input=True, confirmation_prompt=True, help='The password used to login.')
def admin(username, password):
    """创造管理员账号"""
    db.create_all()
    user = User.query.first()
    if user is not None:
        click.echo('Updating user...')
        user.username = username
        user.set_password(password)
    else:
        click.echo('Creating user...')
        user = User(username=username, name='Admin')
        user.set_password(password)
        db.session.add(user)
    db.session.commit()
    click.echo('Done.')


@login_manager.user_loader
def load_user(user_id):
    """创建用户加载回调函数, 接受用户ID作为参数"""
    user = User.query.get(int(user_id))
    return user


@app.route('/home')
@app.route('/index')
@app.route('/hello')
def hello():
    return '<h1>Welcome to My Watchlist</h1> <img src="http://helloflask.com/totoro.gif">'


@app.context_processor
def inject_user():
    user = User.query.first()
    return dict(user=user)  # 等同return {'user': user}


@app.errorhandler(404)  # 使用app.errorhandler()装饰器注册错误处理函数,错误码404
def page_not_found(e):
    """接收异常作为参数"""
    return render_template('404.html'), 404  # 返回模板和状态码


@app.route('/user/<name>')
def user_page(name):
    return 'User: %s' % escape(name)


@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        if not current_user.is_authenticated:
            return redirect(url_for('index'))
        title = request.form.get('title')
        year = request.form.get('year')
        if not title or not year or len(year) > 4 or len(title) > 60:
            flash('Invalid input.')  # 显示错误提示
            return redirect(url_for('index'))  # 重定向回主页
        movie = Movie(title=title, year=year)
        db.session.add(movie)
        db.session.commit()
        flash('Item created.')
        return redirect(url_for('index'))
    movies = Movie.query.all()
    return render_template('index.html', movies=movies)


@app.route('/login', methods=['GET', 'POST'])
def login():
    """登陆逻辑"""
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        if not username or not password:
            flash('Invalid input.')
            return redirect(url_for('login'))
        user = User.query.first()
        # 验证用户名和密码是否一致
        if username == user.username and user.validate_password(password):
            login_user(user)
            flash('Login success.')
            return redirect(url_for('index'))
        flash('Invalid username or password.')
        return redirect(url_for('login'))
    return render_template('login.html')


@app.route('/logout')
@login_required
def logout():
    """登出用户"""
    logout_user()
    flash('Goodbye.')
    return redirect(url_for('index'))


@app.route('/settings', methods=['GET', 'POST'])
@login_required
def settings():
    if request.method == 'POST':
        name = request.form['name']
        if not name or len(name) > 20:
            flash('Invalid input.')
            return redirect(url_for('settings'))
        current_user.name = name
        db.session.commit()
        flash('Settings updated.')
        return redirect(url_for('index'))
    return render_template('settings.html')


@app.route('/movie/edit/<int:movie_id>', methods=['GET', 'POST'])
@login_required  # 登陆保护, 未登陆用户不允许访问
def edit(movie_id):
    """编辑movie信息"""
    movie = Movie.query.get_or_404(movie_id)
    if request.method == 'POST':
        title = request.form['title']
        year = request.form['year']
        if not title or not year or len(year) > 4 or len(title) > 60:
            flash('Invalid input.')
            return redirect(url_for('edit', movie_id=movie_id))  # 重定向到编辑页面（当前页面）
        movie.title = title
        movie.year = year
        db.session.commit()
        flash('Item updated.')
        return redirect(url_for('index'))
    return render_template('edit.html', movie=movie)


@app.route('/movie/delete/<int:movie_id>', methods=['GET', 'POST'])
@login_required  # 登陆保护, 未登陆用户不允许访问
def delete(movie_id):
    """删除movie信息"""
    movie = Movie.query.get_or_404(movie_id)
    db.session.delete(movie)
    db.session.commit()
    flash('Item deleted')
    return redirect(url_for('index'))


@app.route('/test')
def test_url_for():
    print(url_for('hello'))
    print(url_for('user_page', name='hanqingqing'))
    print(url_for('test_url_for'))
    print(url_for('test_url_for', user='zhuliuting'))
    return 'Test page'
