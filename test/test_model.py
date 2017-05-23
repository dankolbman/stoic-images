import json

from flask import current_app, url_for
from test.utils import FlaskTestCase, api_headers
from images.model import Image


class ModelTestCase(FlaskTestCase):

    def test_image(self):
        """
        Test image model
        """
        img = Image(username='Dan')
        self.assertEqual(img.username, 'Dan')
