# Simple backend for a wiki.

My first Flask application :)

Developed against Python 3.4.2 with Flask 0.12.2 on Debian 8.
Also tested using Python 2.7.9 on Debian, and Python 3.4.3 on Windows 10 64 bit.

## Unit tests

Run

    python3 wiki_tests.py

## Trying it out interactively

### Starting on Windows

    virtualenv venv
    venv\Scripts\activate
    pip install --editable .
    set FLASK_APP=wiki\wiki.py
    set FLASK_DEBUG=true # don't do this on a production server
    flask run

### Starting on Linux

(This will probably also work on Mac OS X; I haven't checked yet).

### Exercising the server using curl

After successfully starting the server above, you can try it using curl.
These commands work the same on Linux and Windows if you have curl installed.
(Interestingly single quote escaping on the JSON values won't work on
Windows). These commands assume the server started on port 5000.


    curl http://127.0.0.1:5000/documents # should return []
    curl -H "Content-Type: application/json" http://127.0.0.1:5000/documents/test -d "{\"content\":\"hello\"}"
    curl http://127.0.0.1:5000/documents # should now show test
    curl http://127.0.0.1:5000/documents/test # should show at least one timestamp
    curl http://127.0.0.1:5000/documents/test/latest








