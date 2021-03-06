import os
import uuid
import time
from datetime import datetime
from dateutil import parser
from flask import request, current_app, abort
from flask_restplus import Api, Resource, Namespace, fields
from flask_jwt import _jwt_required, JWTError, current_identity

from .. import db
from ..model import Image


api = Namespace('image', description='Image service')


image_model = api.model('Image', {
        'id': fields.Integer(description='Image id'),
        'trip_id': fields.Integer(description='Trip id'),
        'username': fields.String(description='username'),
        'basepath': fields.String(description='Location of the file'),
        'paths': fields.Raw(description='Image paths'),
        'created_at': fields.DateTime(description='Time of creation'),
        'lon': fields.Float(description='Longitude'),
        'lat': fields.Float(description='Latitude'),
        'caption': fields.String(description='Caption'),
        'location': fields.String(description='Geocoded location'),
        'width': fields.Float(description='Width in pixels'),
        'height': fields.Float(description='Height in pixels'),
    })


paginated = api.model('Response', {
        'images': fields.List(fields.Nested(image_model)),
        'total': fields.Integer(description='number of results')
    })


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


@api.route('/<string:username>/<string:trip_id>')
@api.doc(params={'username': 'username', 'trip_id': 'numeric trip id'})
class ImageByTrip(Resource):
    @api.doc(responses={400: 'missing fields', 201: 'image created'})
    def post(self, username, trip_id):
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
        if ext.lower() not in current_app.config['ALLOWED_IMAGES']:
            return {'status': 400, 'message': 'invalid file type'}, 400

        iid = str(uuid.uuid5(uuid.NAMESPACE_URL,
                             image.filename + str(time.time())))
        filepath = '/'.join([username,
                             trip_id,
                             iid + '.' + ext])

        path = os.path.join(current_app.config['IMAGE_UPLOAD_DIR'],
                            filepath)
        os.makedirs('/'.join(path.split('/')[:-1]), exist_ok=True)
        image.save(path)

        img = Image(username=username, trip_id=trip_id, basepath=path)
        db.session.add(img)
        db.session.commit()
        # doing this now allows us to lose db session scope and call the task
        img_js = img.to_json()

        from ..tasks.metadata import extract
        from ..tasks.resize import resize
        chain = (extract.s(img_js['id']) | resize.s())
        task_id = str(chain())

        return {'message': 'uploaded image for processing',
                'image': img_js,
                'task_id': task_id}, 201

    @api.doc(responses={200: 'found images', 404: 'no images found'})
    @api.marshal_with(paginated)
    def get(self, username, trip_id):
        """
        List images for a given trip
        """
        now = datetime.utcnow().isoformat()
        before = request.args.get('before', now, type=str)
        before_dt = parser.parse(before)
        size = min(request.args.get('size', 10, type=int), 1000)

        q = (Image.query.filter_by(username=username)
                        .filter_by(trip_id=trip_id)
                        .filter(Image.created_at < before_dt)
                        .order_by(Image.created_at.desc()))
        total = q.count()
        if total == 0:
            abort(404, 'no images found for this user and trip')
        images = q.limit(size)
        return {'images': images, 'total': total}, 200


@api.route('/<string:username>/<string:trip_id>/<int:id>')
@api.doc(params={'username': 'username',
                 'trip_id': 'numeric trip id',
                 'id': 'the image id'})
class ImageById(Resource):
    @api.doc(responses={400: 'missing fields', 201: 'image created'})
    def delete(self, username, trip_id, id):
        """
        Delete an image
        """
        # check the trip belongs to the authenticated user
        allowed = belongs_to(username)
        if allowed is not True:
            return allowed
        im = Image.query.get(id)
        for path in im.paths.values():
            os.remove(path)
        basepath = os.path.join(current_app.config['IMAGE_UPLOAD_DIR'],
                                im.basepath)
        os.remove(basepath)
        db.session.delete(im)
        db.session.commit()


@api.route('/<string:username>')
@api.doc(params={'username': 'username'})
class ImageByUser(Resource):
    @api.doc(responses={200: 'found images', 404: 'no images found'})
    @api.marshal_with(paginated)
    def get(self, username):
        """
        List images for a given user
        """
        now = datetime.utcnow().isoformat()
        before = request.args.get('before', now, type=str)
        before_dt = parser.parse(before)
        size = min(request.args.get('size', 10, type=int), 1000)

        q = (Image.query.filter_by(username=username)
                        .filter(Image.created_at < before_dt)
                        .order_by(Image.created_at.desc()))
        total = q.count()
        if total == 0:
            abort(404, 'no images found for this user')
        images = q.limit(size)
        return {'images': images, 'total': total}, 200
