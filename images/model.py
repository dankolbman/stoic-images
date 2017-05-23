from werkzeug.security import generate_password_hash, check_password_hash

from . import db


class Image(db.Model):
    """
    The image model
    """
    __tablename__ = 'images'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(32), index=True)
    path_raw = db.Column(db.String(256))
    path_64x64 = db.Column(db.String(256))
    path_128x128 = db.Column(db.String(256))
    path_640x480 = db.Column(db.String(256))
    path_1280x960 = db.Column(db.String(256))

    def to_json(self):
        return {"id": self.id,
                "username": self.username,
                "path_raw": self.path_raw,
                "path_32x32": self.path_32x32,
                "path_64x64": self.path_64x64,
                "path_128x128": self.path_128x128,
                "path_640x480": self.path_640x480,
                "path_1280x960": self.path_1280x960}
