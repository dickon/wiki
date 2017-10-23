from flask import Flask, request
from json import dumps
from os.path import join
app = Flask(__name__)

@app.route("/documents")
def documents():
    return dumps([])

@app.route("/documents/<name>", methods=['POST'])
def post_page(name):
    # TODO: validate name
    with open(join(app.config['ROOT'], name), 'wb') as f:
        f.write(request.data)
        return 'saved'

@app.route("/documents/<name>/latest", methods=['GET'])
def get_latest_page(name):
    # TODO: validate name
    with open(join(app.config['ROOT'], name), 'r') as f:
        return dumps({'content':f.read()})

        
