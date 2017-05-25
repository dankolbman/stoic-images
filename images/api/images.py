import os
import uuid
import time
from flask import request, current_app
from flask_restplus import Api, Resource, Namespace, fields
from flask_jwt import _jwt_required, JWTError, current_identity

from .. import db
from ..model import Image


api = Namespace('image', description='Image service')


def belongs_to(username):
    try:
        _jwt_required(None)
        if not current_identity['username'] == username:
            return {'status': 403, 'message': 'not allowed'}, 403
    except JWTError as e:
        return {'status': 403, 'message': 'not allowed'}, 403

    return True


@api.route('/status')
class Status(Resource):
    def get(self, **kwargs):
        return {'status': 200,
                'version': '1.0'}, 200


@api.route('/<string:username>/<string:tripid>')
class NewImage(Resource):
    @api.doc(responses={400: 'missing fields', 201: 'image created'})
    def post(self, username, tripid):
        """
        Upload an image
        """
        # check the trip belongs to the authenticated user
        allowed = belongs_to(username)
        if allowed is not True:
            return allowed
        # check that there is a file in the request
        if 'file' not in request.files or request.files['file'].filename == '':
            return {'status': 400, 'message': 'no file'}, 400
        image = request.files['file']
        ext = image.filename.split('.')[-1]
        if ext not in current_app.config['ALLOWED_IMAGES']:
            return {'status': 400, 'message': 'invalid file type'}, 400

        iid = str(uuid.uuid5(uuid.NAMESPACE_URL,
                             image.filename + str(time.time())))
        filepath = '/'.join([username,
                             tripid,
                             iid + '.' + ext])

        path = os.path.join(current_app.config['IMAGE_UPLOAD_DIR'],
                            filepath)
        os.makedirs('/'.join(path.split('/')[:-1]), exist_ok=True)
        image.save(path)

        img = Image(username=username, tripid=tripid, basepath=filepath)
        db.session.add(img)
        db.session.commit()

        return {'status': 201,
                'message': 'uploaded image for processing',
                'task_id': 1}, 201


@api.route('/<path:url>')
class ImageByURL(Resource):
    @api.doc(responses={404: 'no image found', 200: 'image found'})
    def get(self, url):
        """
        Return an image by URL
        """
        return {'message': 'image found'}, 200
