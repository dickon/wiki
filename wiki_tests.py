from unittest import TestCase, main
from wiki import APP
from os import close, unlink
from tempfile import mkdtemp
from json import loads, dumps
from shutil import rmtree
from time import time

class WikiTestCase(TestCase):
    def setUp(self):
        APP.testing = True
        APP.config['ROOT'] = mkdtemp()
        self.APP = APP.test_client()
        
    def tearDown(self):
        rmtree(APP.config['ROOT'])

    def get_json(self, path):
        return loads(self.APP.get(path).data.decode())
        
    def test_empty(self):
        empty_list = self.get_json('/documents')
        assert empty_list == []

    def test_single_page(self):
        first_version = 'hello world'
        second_version = 'Hello, world!'
        rv = self.APP.post('/documents/test', data=dumps({'content':first_version}))
        assert rv.status_code == 200
        wanted_page = self.get_json('/documents/test/latest')
        assert wanted_page == {'content': first_version}
        one_doc = self.get_json('/documents')
        assert one_doc == [{'title':'test'}]
        doc_versions = self.get_json('/documents/test')
        assert len(doc_versions) == 1
        assert abs(time() - float(doc_versions[0]['timestamp_string'])) < 3.0
        rv = self.APP.post('/documents/test', data=dumps({'content':second_version}))
        ts_page = self.get_json('/documents/test/'+doc_versions[0]['timestamp_string'])
        assert ts_page == {'content': first_version}
        updated_page = self.get_json('/documents/test/latest')
        assert updated_page == {'content': second_version}
        
    def test_invalid_title(self):
        rv = self.APP.get('/documents/&#47;&#46;&#46.hack/latest')
        assert rv.status_code == 400 # never actually gets to our code, the routing retursns 405/Method not allowed
        rv2 = self.APP.get('/documents/waywaywaywaywaywaywaywaywaywaywaywaywaywaywaywaywaywaywaywaywaywaywaywaytoolong/latest')
        assert rv2.status_code == 400

    def test_malformed_json_page(self):
        rv = self.APP.post('/documents/test', data="{'content':bad)")
        assert rv.status_code == 400
        
class WikiUnconfigured(TestCase):
    def test_unconfigured(self):
        app = APP.test_client()
        rv = app.get('/documents')
        # depending on what order this runs it may be that ROOT got set up in the APP
        # config by executions of WikiTestCase, in which case the tearDown should have
        # deleted the data so that will cause the server to detect the missing data to 500
        # Or, we run first and ROOT never got set which also should make the server return 500
        assert rv.status_code == 500

if __name__ == '__main__':
    main()
