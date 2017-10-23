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

    def get_json(self, path):
        return loads(self.app.get(path).data.decode())
        
    def test_empty(self):
        empty_list = self.get_json('/documents')
        assert empty_list == []

    def test_single_page(self):        
        rv = self.app.post('/documents/test', data='hello world')
        assert rv.status_code == 200
        wanted_page = self.get_json('/documents/test/latest')
        assert wanted_page == {'content': 'hello world'}
    
        
if __name__ == '__main__':
    main()
