# -*- coding:utf-8 -*-
from flask import render_template

from watchlist import app


@app.errorhandler(404)  # 使用app.errorhandler()装饰器注册错误处理函数,错误码404
def page_not_found(e):
    """接收异常作为参数"""
    return render_template('errors/404.html'), 404  # 返回模板和状态码
