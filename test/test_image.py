import os
import json
from datetime import datetime
from flask import current_app, url_for

from images.model import Image

from test.utils import FlaskTestCase


class ImageTestCase(FlaskTestCase):

    def test_status(self):
        """
        Test image status endpoint
        """
        response = self.client.get(url_for('image_status'))
        json_response = json.loads(response.data.decode('utf-8'))
        self.assertEqual(json_response['status'], 200)

    def test_upload(self):
        """
        Test image creation via REST API
        """
        data = dict(file=(open('test/images/BlueMarble.jpeg', 'rb'),
                          "BlueMarble.jpeg"))
        response = self.client.post(
                    url_for('image_new_image', username='Dan', tripid=1),
                    headers=self._api_headers(username='Dan'),
                    content_type='multipart/form-data',
                    data=data),
        json_response = json.loads(response[0].data.decode('utf-8'))
        self.assertEqual(response[0].status, '201 CREATED')
        self.assertIn('task_id', json_response)
        self.assertIn('task_id', json_response)
        # check that the task to insert points and line ran
        self.assertEqual(Image.query.count(), 1)
        self.assertTrue(os.path.isdir('image_uploads/Dan/1'))
        self.assertEqual(len(os.listdir('image_uploads/Dan/1')), 1)

    def test_duplicate(self):
        """
        Test that duplicate uploads dont cause already exists error
        """
        data = dict(file=(open('test/images/BlueMarble.jpeg', 'rb'),
                          "BlueMarble.jpeg"))
        response = self.client.post(
                    url_for('image_new_image', username='Dan', tripid=1),
                    headers=self._api_headers(username='Dan'),
                    content_type='multipart/form-data',
                    data=data)
        data = dict(file=(open('test/images/BlueMarble.jpeg', 'rb'),
                          "BlueMarble.jpeg"))
        response = self.client.post(
                    url_for('image_new_image', username='Dan', tripid=1),
                    headers=self._api_headers(username='Dan'),
                    content_type='multipart/form-data',
                    data=data),
        json_response = json.loads(response[0].data.decode('utf-8'))
        self.assertEqual(response[0].status, '201 CREATED')
        self.assertTrue(os.path.isdir('image_uploads/Dan/1'))
        self.assertEqual(len(os.listdir('image_uploads/Dan/1')), 2)

    def test_no_auth(self):
        """
        Test response when authorization is not passed
        """
        data = dict(file=(open('test/images/BlueMarble.jpeg', 'rb'),
                          "BlueMarble.jpeg"))
        response = self.client.post(
                    url_for('image_new_image', username='Dan', tripid=1),
                    headers=self._api_headers(username='Dannn'),
                    content_type='multipart/form-data',
                    data=data),
        self.assertEqual(response[0].status_code, 403)
        json_response = json.loads(response[0].data.decode('utf-8'))
        self.assertEqual(json_response['status'], 403)

        data = dict(file=(open('test/images/BlueMarble.jpeg', 'rb'),
                          "BlueMarble.jpeg"))
        response = self.client.post(
                    url_for('image_new_image', username='Dan', tripid=1),
                    headers=self._api_headers(),
                    content_type='multipart/form-data',
                    data=data),
        self.assertEqual(response[0].status_code, 403)
        json_response = json.loads(response[0].data.decode('utf-8'))
        self.assertEqual(json_response['status'], 403)

    def test_invalid_format(self):
        """
        Test response for illegal extension type
        """
        data = dict(file=(open('test/utils.py', 'rb'),
                          "utils.py"))
        response = self.client.post(
                    url_for('image_new_image', username='Dan', tripid=1),
                    headers=self._api_headers(username='Dan'),
                    content_type='multipart/form-data',
                    data=data),
        self.assertEqual(response[0].status_code, 400)
        json_response = json.loads(response[0].data.decode('utf-8'))
        self.assertEqual(json_response['status'], 400)
        self.assertEqual(json_response['message'], 'invalid file type')

    def test_no_file(self):
        """
        Test response no file
        """
        response = self.client.post(
                    url_for('image_new_image', username='Dan', tripid=1),
                    headers=self._api_headers(username='Dan'),
                    content_type='multipart/form-data')
        self.assertEqual(response.status_code, 400)
        json_response = json.loads(response.data.decode('utf-8'))
        self.assertEqual(json_response['status'], 400)
        self.assertEqual(json_response['message'], 'no file')
