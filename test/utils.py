import os
import shutil
import json
import jwt
import unittest
from images import create_app, db
from flask import url_for


class FlaskTestCase(unittest.TestCase):
    """ Contains base logic for setting up a Flask app """

    def setUp(self):
        self.app = create_app('testing')
        self.app_context = self.app.app_context()
        self.app_context.push()
        self.client = self.app.test_client()
        db.create_all()
        os.mkdir(self.app.config['IMAGE_UPLOAD_DIR'])

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()
        shutil.rmtree(self.app.config['IMAGE_UPLOAD_DIR'])

    def _api_headers(self, username=None):
        """
        Returns headers for a json request along with a JWT for authenticating
        as a given user
        """
        headers = {
            'Accept': 'application/json',
            'Content-Type': 'application/json',
        }
        if username:
            auth = jwt.encode({"identity": {"username": username},
                               "nbf": 1493862425,
                               "exp": 9999999999,
                               "iat": 1493862425},
                              'secret', algorithm='HS256')
            headers['Authorization'] = 'JWT ' + auth.decode('utf-8')
        return headers

    def _post_images(self, n=1, username='Dan', trip_id=1, fpath=None):
        """ posts a bunch of images """
        if fpath is None:
            fpath = 'test/images/128_128.jpeg'
        for i in range(n):
            data = dict(file=(open(fpath, 'rb'),
                              os.path.basename(fpath)))
            resp = self.client.post(
                    url_for('image_image_by_trip',
                            username=username,
                            trip_id=trip_id),
                    headers=self._api_headers(username=username),
                    content_type='multipart/form-data',
                    data=data)
