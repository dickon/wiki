from json import dumps
from os.path import join, isfile, isdir
from os import listdir, makedirs
from re import compile
from time import time
from flask import Flask, request, abort

APP = Flask(__name__)
DOCUMENT_NAME_REGEXP = compile("[A-Za-z0-9]{1,50}$")
TIMESTAMP_REGEXP = compile(r"\d+(\.\d+)?$")

# library functions

def get_version_directories(name):
    page_directory = join(APP.config['ROOT'], name)
    unsorted = [x for x in listdir(page_directory) if TIMESTAMP_REGEXP.match(x) and isfile(join(page_directory, x))]
    return sorted(unsorted, key=float)

def verify_page_name(name):
    if not DOCUMENT_NAME_REGEXP.match(name):
        abort(400) # if we wanted to require python 3.4 we could use http.HTTPStatus

def verify_root():
    if 'ROOT' not in APP.config:
        abort(500)
    if not isdir(APP.config['ROOT']):
        abort(500)

# entry points

@APP.route("/documents")
def documents():
    verify_root()
    return dumps(sorted([name for name in listdir(APP.config['ROOT']) if DOCUMENT_NAME_REGEXP.match(name)]))

@APP.route("/documents/<name>", methods=['POST'])
def post_page(name):
    verify_page_name(name)
    page_directory = join(APP.config['ROOT'], name)
    if not isdir(page_directory):
        makedirs(page_directory)
    page_filename = join(page_directory, str(time()))
    with open(page_filename, 'wb') as f:
        f.write(request.data)
        return 'saved'

    
@APP.route("/documents/<name>/latest", methods=['GET'])
def get_latest_page(name):
    verify_page_name(name)
    versions = get_version_directories(name)
    if versions == []:
        abort(404)
    with open(join(APP.config['ROOT'], name, versions[-1]), 'r') as f:
        return dumps({'content':f.read()})

@APP.route("/documents/<name>", methods=['GET'])
def get_page_versions(name):
    verify_page_name(name)
    versions = get_version_directories(name)
    return dumps([{'timestamp_string':x} for x in versions])
