import json
from flask import current_app, url_for
from test.utils import FlaskTestCase
from images.model import Image


class ModelTestCase(FlaskTestCase):

    def test_image(self):
        """
        Test image model
        """
        img = Image(username='Dan', tripid=1, basepath='test/image.jpg')
        self.assertEqual(img.username, 'Dan')
        self.assertEqual(img.tripid, 1)
        self.assertEqual(img.to_json()['paths'], {})
        img = Image(username='Dan', tripid=1, paths={'hello': 'world'})
        self.assertEqual(img.to_json()['paths'], {'hello': 'world'})
