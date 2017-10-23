from json import dumps
from os.path import join
from re import compile
from flask import Flask, request, abort

app = Flask(__name__)
document_name_regexp = compile("[A-Za-z0-9]{1,50}$")


@app.route("/documents")
def documents():
    return dumps([])

@app.route("/documents/<name>", methods=['POST'])
def post_page(name):
    if not document_name_regexp.match(name):
        abort(400)
    # TODO: validate name
    with open(join(app.config['ROOT'], name), 'wb') as f:
        f.write(request.data)
        return 'saved'

@app.route("/documents/<name>/latest", methods=['GET'])
def get_latest_page(name):
    if not document_name_regexp.match(name):
        abort(400)
    # TODO: validate name
    with open(join(app.config['ROOT'], name), 'r') as f:
        return dumps({'content':f.read()})

        
