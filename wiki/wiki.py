"""A simple Wiki API using JSON; see ./wiki_tests.py for test cases.

Uses flask (http://flask.pocoo.org/)
"""

from json import loads, dumps
from os.path import join, isfile, isdir, join
from tempfile import gettempdir
from os import listdir, makedirs, rename
from re import compile as regexp_compile
from time import time
from functools import wraps
from flask import Flask, request, abort, Response, jsonify

APP = Flask(__name__)
APP.config.update(dict(ROOT=join(gettempdir(),"wikidata")))
APP.config.from_envvar('WIKI_SETTINGS', silent=True)

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
    if not isdir(page_directory):
        abort(404)
    unsorted = [x for x in listdir(page_directory) if
                TIMESTAMP_REGEXP.match(x) and isfile(join(page_directory, x))]
    return sorted(unsorted, key=float)

def error(description, code=500, **keywords):
    """Produce a response:

    Args:
       code (int): HTTP response code
       description (str): problem description text
       other arguments are added to the JSON response dictionary.

    Returns:
       Response: a Flask Response instance
    """
    resp = dict(problem=description, **keywords)
    return Response(dumps(resp), status=code, content_type='application/json')

    
def check_and_json_encode(func):
    # we need functools.wraps to stack decorators, see
    #  http://flask.pocoo.org/docs/0.12/patterns/viewdecorators/
    @wraps(func)
    def decorated(*args, **kwargs):
        if 'ROOT' not in APP.config:
            return "ROOT not set in config" # should be unreachable now we set a default ROOT
        if not isdir(APP.config['ROOT']):
            try:
                makedirs(APP.config['ROOT'])
            except OSError:
                return error('Unable to create server data directory')
        if 'title' in kwargs:
            if not DOCUMENT_TITLE_REGEXP.match(kwargs['title']):
                return error('illegal document title - regexp mismatch', 400,
                             regexp=DOCUMENT_TITLE_REGEXP.pattern)
        res = func(*args, **kwargs)
        return res if isinstance(res, Response) else jsonify(res)
    return decorated
        
# entry points

@APP.route("/documents")
@check_and_json_encode
def documents():
    """Return a list of available titles.

    Returns:
      str: JSON encoded list of titles, each of which is of the form
           {"title": "pagename"}
           Sample output with one page called test:

              [{"title": "test"}]
    """
    if not isdir(APP.config['ROOT']):
        return jsonify([])
    files = listdir(APP.config['ROOT'])
    return sorted([{"title":title} for title in files if
                   DOCUMENT_TITLE_REGEXP.match(title)])

@APP.route("/documents/<title>", methods=['POST'])
@check_and_json_encode
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
    filename = join(page_directory, timestamp)

    try:
        with open(filename+'.t', 'w') as fileobj:
            fileobj.write(doc['content'])
    except IOError:
        return error('unable to write page')
    try:
        rename(filename+'.t', filename)
    except OSError:
        return error('unable to rename filne in to place; try again')
    
    return {'timestamp_string':timestamp}

@APP.route("/documents/<title>/<timestamp>", methods=['GET'])
@check_and_json_encode
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
    versions = get_version_directories(title)
    if timestamp == 'latest':
        if versions == []:
            abort(404)
        version = versions[-1]
    else:
        if timestamp not in versions:
            abort(404)
        version = timestamp
    try:
        with open(join(APP.config['ROOT'], title, version), 'r') as fileobj:
            return {'content':fileobj.read()}
    except IOError(exc):
        APP.logger.error(exc)
        return error('unable to read page content', 503)

@APP.route("/documents/<title>", methods=['GET'])
@check_and_json_encode
def get_page_versions(title):
    """Return all the timestamps for a page.

    Args:
      title(str): the page title

    Returns:
      str: JSON encoded list of objects with timestamp_string fields, such as:
      [{"timestamp_version":"123.4", "timestamp_version": "456"}]
    """        
    versions = get_version_directories(title)
    return [{'timestamp_string':x} for x in versions]
