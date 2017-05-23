from flask import request, jsonify, session
from ..model import Image
from flask_restplus import Api, Resource, Namespace, fields
from .. import db


api = Namespace('image', description='Image service')


@api.route('/status')
class Status(Resource):
    def get(self, **kwargs):
        return {'status': 200,
                'version': '1.0'}, 200


@api.route('/')
class NewImage(Resource):
    @api.doc(responses={400: 'missing fields', 201: 'image created'})
    def post(self, **kwargs):
        """
        Upload an image
        """
        return {'message': 'image created'}, 201


@api.route('/<string:url>')
class ImageByURL(Resource):
    @api.doc(responses={404: 'no image found', 200: 'image found'})
    def get(self, url):
        """
        Return an image by URL
        """
        return {'message': 'image found'}, 200
