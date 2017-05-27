import os
from flask import url_for

from images.model import Image as Image

from test.utils import FlaskTestCase


class TaskTestCase(FlaskTestCase):

    def test_metadata_extract(self):
        """
        Test that image metadata is extracted and put into the image model
        """
        self._post_images(n=1, fpath='test/images/BlueMarble.jpeg')
        path = '/Users/dan/Desktop/20150611_164147_22942009824_o.jpg'
        self.assertEqual(Image.query.count(), 1)
        img = Image.query.first()
        print(img.to_json())



        #self._post_images(n=1, fpath=path)
        #path = '/Users/dan/Desktop/IMG_20170429_182453903.jpg'
        #self._post_images(n=1, fpath=path)
        #path = '/Users/dan/Desktop/YDXJ0020.JPG'
        #self._post_images(n=1, fpath=path)
