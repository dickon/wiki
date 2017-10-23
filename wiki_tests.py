from unittest import TestCase, main
from wiki import app
from tempfile import mkstemp
from os import close, unlink

class WikiTestCase(TestCase):
    def setUp(self):
        app.testing = True
        self.app = app.test_client()
            
    def test_empty(self):
        rv = self.app.get('/documents')
        print(rv.data)
        assert rv.data == b"[]"
        pass
    
if __name__ == '__main__':
    main()
