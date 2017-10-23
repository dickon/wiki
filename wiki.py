from flask import Flask
from json import dumps

app = Flask(__name__)

@app.route("/documents")
def documents():
    return dumps([])

@app.route("/documents/<name>", methods=['POST'])
def page(name):
    return dumps({'content':''})

