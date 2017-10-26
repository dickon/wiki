"""A simple Wiki API using JSON; see ./wiki_tests.py for test cases.

Uses flask (http://flask.pocoo.org/)
"""

from json import dumps, loads
from os.path import join, isfile, isdir
from os import listdir, makedirs
from re import compile as regexp_compile
from time import time
from flask import Flask, request, abort, Response, jsonify

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
    # TODO: cope with page_directory being missing
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
      str: JSON encoded list of titles, each of which is of the form
           {"title": "pagename"}
           Sample output with one page called test:

              [{"title": "test"}]
    """
    verify_root()
    files = listdir(APP.config['ROOT'])
    return jsonify(sorted([{"title":title} for title in files if
                           DOCUMENT_TITLE_REGEXP.match(title)]))

@APP.route("/documents/<title>", methods=['POST'])
def post_page(title):
    """Post a new page, obtained from the flask request data.

    The request data should be of the form:
       { "content": "Hello world" }

    Args:
      title(str): name of the page

    Returns:
      str: status indicating message, e.g. "saved"

    Can also fail with HTTP code 400 if title is illegal,
    or 500 if server directory root is not configured or write failed.
    """
    verify_root()
    verify_page_title(title)
    try:
        # note that request here is thread local, see:
        #   http://flask.pocoo.org/docs/0.12/quickstart/#the-request-object
        doc = loads(request.data.decode())
    except ValueError:
        abort(400) # TODO: specific error text saying JSON is invalid?

    # TODO: validate doc structure
    page_directory = join(APP.config['ROOT'], title)
    if not isdir(page_directory):
        makedirs(page_directory)
    timestamp = str(time())
    page_filetitle = join(page_directory, timestamp)
    # TODO: catch file errors
    with open(page_filetitle, 'w') as fileobj:
        fileobj.write(doc['content'])
        return jsonify({'timestamp_string':timestamp})

@APP.route("/documents/<title>/<timestamp>", methods=['GET'])
def get_specific_page(title, timestamp):
    """Return the content of a specific page at a given timestamp:

    Args:
      title(str): the page title
      timestamp: either a numeric timestamp or the string "latest"

    Returns:
      str: JSON encoded object with key "content" and value being the page value

    Can also fail with HTTP code 404 for timestamp or page not found,
    or 500 if this app has not been configured with a page.
    """

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
    with open(join(APP.config['ROOT'], title, version), 'r') as fileobj:
        return jsonify({'content':fileobj.read()})

@APP.route("/documents/<title>", methods=['GET'])
def get_page_versions(title):
    """Return all the timestamps for a page.

    Args:
      title(str): the page title

    Returns:
      str: JSON encoded list of objects with timestamp_string fields, such as:
      [{"timestamp_version":"123.4", "timestamp_version": "456"}]
    """
    verify_root()
    verify_page_title(title)
    versions = get_version_directories(title)
    return dumps([{'timestamp_string':x} for x in versions])
