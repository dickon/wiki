from json import dumps
from os.path import join
from os import listdir
from re import compile
from flask import Flask, request, abort

APP = Flask(__name__)
DOCUMENT_NAME_REGEXP = compile("[A-Za-z0-9]{1,50}$")


@APP.route("/documents")
def documents():
    return dumps(sorted([name for name in listdir(APP.config['ROOT']) if DOCUMENT_NAME_REGEXP.match(name)]))

@APP.route("/documents/<name>", methods=['POST'])
def post_page(name):
    if not DOCUMENT_NAME_REGEXP.match(name):
        abort(400) # if we wanted to require python 3.4 we could use http.HTTPStatus
    with open(join(APP.config['ROOT'], name), 'wb') as f:
        f.write(request.data)
        return 'saved'

@APP.route("/documents/<name>/latest", methods=['GET'])
def get_latest_page(name):
    if not DOCUMENT_NAME_REGEXP.match(name):
        abort(400)
    with open(join(APP.config['ROOT'], name), 'r') as f:
        return dumps({'content':f.read()})

        
