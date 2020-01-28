# -*- coding:utf-8 -*-
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

from watchlist import db


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
