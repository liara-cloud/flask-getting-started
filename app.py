from flask import Flask, render_template
from flask_pymongo import PyMongo
import json
import os
app = Flask(__name__)


@app.route('/')
def hello_world():
    return render_template('index.html')


@app.route('/envs')
def show_envs():
    return os.getenv('LIARA_URL', 'LIARA_URL not set!')


@app.route('/mongodb')
def mongodb():
    if(os.getenv('MONGO_URI') is None):
        return 'MONGO_URI not set!'
    mongo = PyMongo(app, uri=os.getenv('MONGO_URI'))
    name = mongo.db.name
    return 'currnet db name is: ' + json.dumps(name)
