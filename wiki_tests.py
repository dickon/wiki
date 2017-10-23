from unittest import TestCase, main
from wiki import app
from os import close, unlink
from tempfile import mkdtemp
from json import loads
from shutil import rmtree

class WikiTestCase(TestCase):
    def setUp(self):
        app.testing = True
        app.config['ROOT'] = mkdtemp()
        self.app = app.test_client()
        
    def tearDown(self):
        rmtree(app.config['ROOT'])
        
    def test_empty(self):
        rv = self.app.get('/documents')
        assert rv.data == b"[]"
        out = loads(rv.data.decode())
        assert out == []

    def test_single_page(self):
        rv = self.app.post('/documents/test', data='hello world')
        assert rv.status_code == 200
        rv2 = self.app.get('/documents/test/latest')
        out2 = loads(rv2.data.decode())
        assert out2['content'] == 'hello world'
    
        
if __name__ == '__main__':
    main()
