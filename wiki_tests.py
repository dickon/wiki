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
        one_doc = self.get_json('/documents')
        assert one_doc == ['test']
        
    def test_invalid_title(self):
        rv = self.app.get('/documents/&#47;&#46;&#46.hack/latest')
        assert rv.status_code == 400 # never actually gets to our code, the routing retursns 405/Method not allowed
        rv2 = self.app.get('/documents/waywaywaywaywaywaywaywaywaywaywaywaywaywaywaywaywaywaywaywaywaywaywaywaytoolong/latest')
        assert rv2.status_code == 400
        


if __name__ == '__main__':
    main()
