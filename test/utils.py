import json
import unittest
from images import create_app, db


class FlaskTestCase(unittest.TestCase):
    """ Contains base logic for setting up a Flask app """

    def setUp(self):
        self.app = create_app('testing')
        self.app_context = self.app.app_context()
        self.app_context.push()
        self.client = self.app.test_client()
        db.create_all()

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()


def api_headers():
    """
    Headers for json request
    """
    return {
        'Accept': 'application/json',
        'Content-Type': 'application/json'
    }
