"""A simple Wiki API using JSON; see ./wiki_tests.py for test cases"""
from json import dumps, loads
from os.path import join, isfile, isdir
from os import listdir, makedirs
from re import compile as regexp_compile
from time import time
from flask import Flask, request, abort

APP = Flask(__name__)
DOCUMENT_TITLE_REGEXP = regexp_compile("[A-Za-z0-9]{1,50}$")
TIMESTAMP_REGEXP = regexp_compile(r"\d+(\.\d+)?$")

# library functions

def get_version_directories(title):
    """Return a list of version strings for a page:

    Args:
       title (str): page title, assumed to be verified

    Returns:
       List[str]: list of timestamps in string form, sorted in 
                  floating point numeric order
    """
    
    page_directory = join(APP.config['ROOT'], title)
    unsorted = [x for x in listdir(page_directory) if
                TIMESTAMP_REGEXP.match(x) and isfile(join(page_directory, x))]
    return sorted(unsorted, key=float)

def verify_page_title(title):
    """Check that title is valid, or abort (raising an exception)"

    Args:
      title (str): page title
    """
    if not DOCUMENT_TITLE_REGEXP.match(title):
        # TODO: if we wanted to require python 3.4 we could use http.HTTPStatus
        abort(400)

def verify_root():
    """Check that the site has been properly configured, and if not call flask's 
    abort, raising an exception."""
    if 'ROOT' not in APP.config:
        abort(500)
    if not isdir(APP.config['ROOT']):
        abort(500)

# entry points

@APP.route("/documents")
def documents():
    """Return a list of available titles.

    Returns:
      str: JSON encoded list of titles
    """
    verify_root()
    return dumps(sorted([{"title":title} for title in listdir(APP.config['ROOT']) if
                         DOCUMENT_TITLE_REGEXP.match(title)]))

@APP.route("/documents/<title>", methods=['POST'])
def post_page(title):
    verify_root()
    verify_page_title(title)
    try:
        doc = loads(request.data.decode())
    except ValueError:
        abort(400) # TODO: specific error text saying JSON is invalid?

    # TODO: validate doc structure
    page_directory = join(APP.config['ROOT'], title)
    if not isdir(page_directory):
        makedirs(page_directory)
    page_filetitle = join(page_directory, str(time()))
    with open(page_filetitle, 'w') as f:
        f.write(doc['content'])
        return 'saved'

@APP.route("/documents/<title>/<timestamp>", methods=['GET'])
def get_specific_page(title, timestamp):
    verify_root()
    verify_page_title(title)
    versions = get_version_directories(title)
    if timestamp == 'latest':
        if versions == []:
            abort(404)
        version = versions[-1]
    else:
        if timestamp not in versions:
            abort(404)
        version = timestamp
    with open(join(APP.config['ROOT'], title, version), 'r') as f:
        return dumps({'content':f.read()})

@APP.route("/documents/<title>", methods=['GET'])
def get_page_versions(title):
    verify_root()
    verify_page_title(title)
    versions = get_version_directories(title)
    return dumps([{'timestamp_string':x} for x in versions])
