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
        response = self.client.get(url_for('status'))
        json_response = json.loads(response.data.decode('utf-8'))
        self.assertEqual(json_response['status'], 200)
        self.assertEqual(len(json_response['version']), 7)

    def test_upload(self):
        """
        Test image creation via REST API
        """
        data = dict(file=(open('test/images/BlueMarble.jpeg', 'rb'),
                          "BlueMarble.jpeg"))
        response = self.client.post(
                    url_for('image_image_by_trip', username='Dan', trip_id=1),
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
        self.assertEqual(len(os.listdir('image_uploads/Dan/1')), 7)
        response = self.client.get(
                    url_for('image_image_by_trip', username='Dan', trip_id=1))
        json_response = json.loads(response.data.decode('utf-8'))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(json_response['total'], 1)
        self.assertEqual(len(json_response['images']), 1)
        self.assertEqual(type(json_response['images'][0]['paths']), dict)
        self.assertEqual(json_response['images'][0]['id'], 1)

    def test_delete(self):
        """
        Test deleteing an image
        """
        self._post_images(n=1, username='Dan', trip_id=1)
        self.assertEqual(Image.query.count(), 1)
        response = self.client.delete(
                    url_for('image_image_by_id',
                            username='Dan', trip_id=1, id=1))
        self.assertEqual(response.status_code, 403)
        self.assertEqual(len(os.listdir('image_uploads/Dan/1')), 7)
        response = self.client.delete(
                    url_for('image_image_by_id',
                            username='Dan', trip_id=1, id=1),
                    headers=self._api_headers(username='Dan'))
        self.assertEqual(Image.query.count(), 0)
        self.assertEqual(len(os.listdir('image_uploads/Dan/1')), 0)

    def test_many(self):
        """
        Test serveral images from different trips and users
        """
        self._post_images(n=1, username='dan', trip_id=1)
        self._post_images(n=2, username='dan', trip_id=2)
        self._post_images(n=5, username='bob', trip_id=4)
        self._post_images(n=3, username='dan', trip_id=3)
        self._post_images(n=7, username='bob', trip_id=5)

        response = self.client.get(
                    url_for('image_image_by_trip', username='anon', trip_id=1))
        self.assertEqual(response.status_code, 404)
        response = self.client.get(
                    url_for('image_image_by_user', username='anon'))
        self.assertEqual(response.status_code, 404)
        response = self.client.get(
                    url_for('image_image_by_trip', username='dan', trip_id=2))
        jsonr = json.loads(response.data.decode('utf-8'))
        self.assertEqual(jsonr['total'], 2)
        response = self.client.get(
                    url_for('image_image_by_trip', username='bob', trip_id=5))
        jsonr = json.loads(response.data.decode('utf-8'))
        self.assertEqual(jsonr['total'], 7)
        response = self.client.get(
                    url_for('image_image_by_user', username='dan'))
        jsonr = json.loads(response.data.decode('utf-8'))
        self.assertEqual(jsonr['total'], 6)
        response = self.client.get(
                    url_for('image_image_by_user', username='bob'))
        jsonr = json.loads(response.data.decode('utf-8'))
        self.assertEqual(jsonr['total'], 12)
        self.assertEqual(len(jsonr['images']), 10)

    def test_ordering(self):
        """
        Test that images are returned with newest first
        """
        self._post_images(n=1, username='dan', trip_id=1)
        self._post_images(n=2, username='dan', trip_id=2)
        self._post_images(n=5, username='bob', trip_id=4)
        self._post_images(n=3, username='dan', trip_id=2)
        self._post_images(n=7, username='bob', trip_id=3)

        response = self.client.get('/image/dan/2')
        json_resp = json.loads(response.data.decode('utf-8'))
        self.assertEqual(json_resp['total'], 5)
        dts = [image['created_at'] for image in json_resp['images']]
        self.assertTrue(all([dts[i] > dts[i+1] for i in range(len(dts)-1)]))

        response = self.client.get('/image/dan')
        json_resp = json.loads(response.data.decode('utf-8'))
        dts = [image['created_at'] for image in json_resp['images']]
        self.assertTrue(all([dts[i] > dts[i+1] for i in range(len(dts)-1)]))

    def test_before_param(self):
        """
        Test using `before` param to select time ranges of images
        """
        self._post_images(n=1, username='dan', trip_id=1)
        self._post_images(n=4, username='dan', trip_id=2)
        now = datetime.utcnow().isoformat()
        self._post_images(n=3, username='dan', trip_id=1)
        self._post_images(n=2, username='dan', trip_id=3)

        response = self.client.get('/image/dan/1')
        json_resp = json.loads(response.data.decode('utf-8'))
        self.assertEqual(json_resp['total'], 4)

        response = self.client.get('/image/dan/1?before={}'.format(now))
        json_resp = json.loads(response.data.decode('utf-8'))
        self.assertEqual(json_resp['total'], 1)

        response = self.client.get('/image/dan')
        json_resp = json.loads(response.data.decode('utf-8'))
        self.assertEqual(json_resp['total'], 10)

        response = self.client.get('/image/dan?before={}'.format(now))
        json_resp = json.loads(response.data.decode('utf-8'))
        self.assertEqual(json_resp['total'], 5)

    def test_duplicate(self):
        """
        Test that duplicate uploads dont cause already exists error
        """
        data = dict(file=(open('test/images/BlueMarble.jpeg', 'rb'),
                          "BlueMarble.jpeg"))
        response = self.client.post(
                    url_for('image_image_by_trip', username='Dan', trip_id=1),
                    headers=self._api_headers(username='Dan'),
                    content_type='multipart/form-data',
                    data=data)
        data = dict(file=(open('test/images/BlueMarble.jpeg', 'rb'),
                          "BlueMarble.jpeg"))
        response = self.client.post(
                    url_for('image_image_by_trip', username='Dan', trip_id=1),
                    headers=self._api_headers(username='Dan'),
                    content_type='multipart/form-data',
                    data=data),
        json_response = json.loads(response[0].data.decode('utf-8'))
        self.assertEqual(response[0].status, '201 CREATED')
        self.assertTrue(os.path.isdir('image_uploads/Dan/1'))
        self.assertEqual(len(os.listdir('image_uploads/Dan/1')), 14)

    def test_no_auth(self):
        """
        Test response when authorization is not passed
        """
        data = dict(file=(open('test/images/BlueMarble.jpeg', 'rb'),
                          "BlueMarble.jpeg"))
        response = self.client.post(
                    url_for('image_image_by_trip', username='Dan', trip_id=1),
                    headers=self._api_headers(username='Dannn'),
                    content_type='multipart/form-data',
                    data=data),
        self.assertEqual(response[0].status_code, 403)
        json_response = json.loads(response[0].data.decode('utf-8'))
        self.assertEqual(json_response['status'], 403)

        data = dict(file=(open('test/images/BlueMarble.jpeg', 'rb'),
                          "BlueMarble.jpeg"))
        response = self.client.post(
                    url_for('image_image_by_trip', username='Dan', trip_id=1),
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
                    url_for('image_image_by_trip', username='Dan', trip_id=1),
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
                    url_for('image_image_by_trip', username='Dan', trip_id=1),
                    headers=self._api_headers(username='Dan'),
                    content_type='multipart/form-data')
        self.assertEqual(response.status_code, 400)
        json_response = json.loads(response.data.decode('utf-8'))
        self.assertEqual(json_response['status'], 400)
        self.assertEqual(json_response['message'], 'no file')
