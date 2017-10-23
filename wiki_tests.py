from unittest import TestCase, main
from wiki import app
from tempfile import mkstemp
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
        
    
if __name__ == '__main__':
    main()
