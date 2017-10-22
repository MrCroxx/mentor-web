# -*- coding:utf-8 -*-

from flask import Flask
app = Flask(__name__)

@app.route('/')
@app.route('/index')
def index():
    return u"<h1>系统维护中... ...</h1>"

app.run(host='0.0.0.0',port=80)