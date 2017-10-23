from unittest import TestCase, main
from wiki import app
from os import close, unlink
from json import loads

class WikiTestCase(TestCase):
    def setUp(self):
        app.testing = True
        self.app = app.test_client()
            
    def test_empty(self):
        rv = self.app.get('/documents')
        assert rv.data == b"[]"
        out = loads(rv.data.decode())
        assert out == []

    def test_single_page(self):
        rv = self.app.post('/documents/test', data='hello world')
        assert rv.status_code == 200

if __name__ == '__main__':
    main()
