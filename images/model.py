from werkzeug.security import generate_password_hash, check_password_hash

from . import db


class Image(db.Model):
    """
    The image model
    """
    __tablename__ = 'images'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(32), index=True)
    tripid = db.Column(db.Integer, index=True)
    basepath = db.Column(db.String(256))
    paths = db.Column(db.JSON(), default={})

    def __init__(self, **kwargs):
        super(Image, self).__init__(**kwargs)
        if 'paths' not in kwargs:
            self.paths = {}

    def to_json(self):
        return {"id": self.id,
                "username": self.username,
                "tripid": self.tripid,
                "basepath": self.basepath,
                "paths": self.paths}
