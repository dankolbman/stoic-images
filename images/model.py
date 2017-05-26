from datetime import datetime
from dateutil import parser
from werkzeug.security import generate_password_hash, check_password_hash

from . import db


class Image(db.Model):
    """
    The image model
    """
    __tablename__ = 'images'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(32), index=True)
    trip_id = db.Column(db.Integer, index=True)
    basepath = db.Column(db.String(256))
    paths = db.Column(db.JSON(), default={})
    created_at = db.Column(db.DateTime(), default=datetime.utcnow())
    lon = db.Column(db.Float)
    lat = db.Column(db.Float)

    def __init__(self, **kwargs):
        if 'created_at' in kwargs and type(kwargs['created_at']) is str:
            kwargs['created_at'] = parser.parse(kwargs['created_at'])
        if 'created_at' not in kwargs:
            kwargs['created_at'] = datetime.utcnow()
        if 'paths' not in kwargs:
            kwargs['paths'] = {}
        super(Image, self).__init__(**kwargs)

    def to_json(self):
        return {"id": self.id,
                "username": self.username,
                "created_at": self.created_at.isoformat(),
                "trip_id": self.trip_id,
                "basepath": self.basepath,
                "paths": self.paths}
