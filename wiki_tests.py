"""Test cases for wiki/wiki.py"""
from unittest import TestCase, main
from wiki import APP
from tempfile import mkdtemp
from json import loads, dumps
from shutil import rmtree
from time import time

class WikiTestCase(TestCase):
    """Test the wiki.py code"""
    def setUp(self):
        """Configure flask server"""
        APP.testing = True
        APP.config['ROOT'] = mkdtemp()
        self.test_client = APP.test_client()

    def tearDown(self):
        """Clear up contents created on filesystem during test"""
        rmtree(APP.config['ROOT'])

    def get_json(self, path):
        """Query content at path on APP and convert to JSON

        Args:
          path(str): path relative to server root

        Returns:
          decoded JSON object
        """
        return loads(self.test_client.get(path).data.decode())

    def test_empty(self):
        """Test that /documents on an empty server returns nothing"""
        empty_list = self.get_json('/documents')
        assert empty_list == []

    def test_single_page(self):
        """Work through a sequence of operations on a single page"""
        first_version = 'hello world'
        second_version = 'Hello, world!'
        res = self.test_client.post('/documents/test',
                                    data=dumps({'content':first_version}))
        assert res.status_code == 200
        assert res.content_type.startswith('application/json')
        wanted_page = self.get_json('/documents/test/latest')
        assert wanted_page == {'content': first_version}
        one_doc = self.get_json('/documents')
        assert one_doc == [{'title':'test'}]
        doc_versions = self.get_json('/documents/test')
        assert len(doc_versions) == 1
        assert abs(time() - float(doc_versions[0]['timestamp_string'])) < 3.0
        res2 = self.test_client.post('/documents/test',
                                     data=dumps({'content':second_version}))
        assert res2.status_code == 200
        ts_page = self.get_json('/documents/test/'+
                                doc_versions[0]['timestamp_string'])
        assert ts_page['content'] == first_version
        updated_page = self.get_json('/documents/test/latest')
        assert updated_page == {'content': second_version}

    def test_invalid_title(self):
        """Check invalid title rejection works"""
        res = self.test_client.get('/documents/&#47;&#46;&#46.hack/latest')
        assert res.status_code == 400
        res2 = self.test_client.get('/documents/waywaywaywaywaywaywaywayway'+
                                    'waywaywaywaywaywaywaywaywaywaywaywayway'+
                                    'toolong/latest')
        assert res2.status_code == 400

    def test_malformed_json_page(self):
        """Try malformed JSON, and check the error code is what's expected"""
        res = self.test_client.post('/documents/test', data="{'content':bad)")
        assert res.status_code == 400

    def test_missing_page(self):
        """Make sure we get a 404 for a missing page"""
        missing_page = self.test_client.get('/documents/test/latest')
        assert missing_page.status_code == 404

if __name__ == '__main__':
    main()
