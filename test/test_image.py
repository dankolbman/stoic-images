import json
import unittest
from datetime import datetime

from flask import current_app, url_for

from test.utils import FlaskTestCase, api_headers


class UserTestCase(FlaskTestCase):

    def test_new_image(self):
        """
        Test image creation via REST API
        """
        pass
