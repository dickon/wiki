# Simple backend for a wiki.

My first Flask application :)

Developed against Python 3.4.2 with Flask 0.12.2 on Debian 8.
Also tested using Python 2.7.9 on Debian, and Python 3.4.3 on Windows 10 64 bit.

## Trying it out interactively

### Starting on Linux

(This will probably also work on Mac OS X; I haven't checked yet).

    virtualenv venv
    . venv/bin/activate
    pip install --editable .
    python wiki_tests.py
    FLASK_APP=wiki FLASK_DEBUG=true flask run # omit FLASK_DEBUG in production

### Starting on Windows

    virtualenv venv
    venv\Scripts\activate
    pip install --editable .
    python wiki_tests.py
    set FLASK_APP=wiki\wiki.py
    set FLASK_DEBUG=true # don't do this on a production server
    flask run

### Exercising the server using curl

After successfully starting the server above, you can try it using curl.
These commands work the same on Linux and Windows if you have curl installed.
(Interestingly single quote escaping on the JSON values won't work on
Windows). These commands assume the server started on port 5000.

    curl http://127.0.0.1:5000/documents # should return []
    curl -H "Content-Type: application/json" http://127.0.0.1:5000/documents/test -d "{\"content\":\"hello\"}"
    curl http://127.0.0.1:5000/documents # should now show test
    curl http://127.0.0.1:5000/documents/test # should show at least one timestamp
    curl http://127.0.0.1:5000/documents/test/latest # or you can use a timestamp float

## Implementaiton notes

The main ways the app can fail have explicit error pages, with JSON
content and suitable HTTP error codes. There are a few ways the server
can throw other exceptions, and in those cases Flask will turn the
abitrary errors into HTTP 500 error pages.

Written to minimise the number of pylint error pages. On a program of
this size I may not have used as many docstring comments as I have
here.

