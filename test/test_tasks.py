import os
from flask import url_for
from unittest.mock import Mock, patch

from images.model import Image as Image

from test.utils import FlaskTestCase


class TaskTestCase(FlaskTestCase):

    @patch('images.tasks.metadata.requests.get')
    def test_interp(self, mock_get):
        """
        Test that image metadata is extracted and put into the image model
        """
        mock_get.return_value.status_code = 200
        js_resp = {'point': {'geometry': {'coordinates': [4.3, 1.30]}}}
        mock_get.return_value.json = lambda: js_resp

        self._post_images(n=1, fpath='test/images/BlueMarble.jpeg')
        self.assertEqual(Image.query.count(), 1)
        img = Image.query.first()
        self.assertEqual(img.created_at.isoformat(), '2005-05-13T13:09:04')
        self.assertEqual(img.width, 3000)
        self.assertEqual(img.height, 3002)
        self.assertEqual(img.lon, 4.3)
        self.assertEqual(img.lat, 1.3)

    def test_gps_exif(self):
        """ Test gps extraction from exif tags """
        path = 'test/images/gps_tag.jpg'
        self._post_images(n=1, fpath=path)
        img = Image.query.first()
        self.assertAlmostEqual(img.lon, -80.562230, 3)
        self.assertAlmostEqual(img.lat, 41.176380, 3)

    def test_resize(self):
        """ Test resizing task """
        self._post_images(n=1, fpath='test/images/wide.jpg')
        self.assertEqual(Image.query.count(), 1)
        img = Image.query.first()
        self.assertEqual(len(img.paths), 6)
        self.assertIn('64x64', img.paths)
        self.assertIn('128x128', img.paths)
        self.assertIn('180h', img.paths)
        self.assertIn('256h', img.paths)
        # should have the original plus the processed files
        self.assertEqual(len(os.listdir('image_uploads/Dan/1')), 7)
        self._post_images(n=1, fpath='test/images/wide.jpg')
        self.assertEqual(Image.query.count(), 2)
        self.assertEqual(len(os.listdir('image_uploads/Dan/1')), 14)

    def test_rotation(self):
        """ Test that images are rotated appropiately """
        self._post_images(n=1, fpath='test/images/tall.jpg')
        self.assertEqual(Image.query.count(), 1)
