from unittest import TestCase
from wiki import app

class WikiTestCase(TestCase):
    def setUp(self):
        app.testing = True
    def test_empty(self):
        rv = self.app.get('/documents')
        assert rv == []

