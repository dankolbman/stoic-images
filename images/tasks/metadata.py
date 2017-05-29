import os
import json
import functools
import requests
from dateutil import parser
import PIL.Image
import PIL.ExifTags
from flask import current_app
from . import celery
from ..model import Image
from images import create_celery_app
from .resize import image_transpose_exif
from .. import db


def parse_gps(exif):
    """
    Converts gps exif tags to decimal degrees lon, lat
    """
    def _to_float(num, den=1):
        if den == 0:
            return 0
        return num / den

    def _to_deg(h, m=0, s=0):
        return h + (m / 60.0) + (s / 3600.0)

    lon = _to_deg(*[_to_float(*v) for v in exif['GPSLongitude']])
    lat = _to_deg(*[_to_float(*v) for v in exif['GPSLatitude']])
    lon = -lon if exif['GPSLongitudeRef'] == 'W' else lon
    lat = -lat if exif['GPSLatitudeRef'] == 'S' else lat
    return lon, lat


def interp_point(username, trip_id, dt):
    """ Will attempt to resolve a point from a datetime using geo service """
    url = ('{}/interp/{}/{}?time={}'
           .format(current_app.config['GEO_URL'],
                   username,
                   trip_id,
                   dt.isoformat()))
    try:
        resp = requests.get(url)
    except requests.exceptions.ConnectionError:
        return None

    if resp.status_code is not 200:
        return None

    js_resp = resp.json()
    return js_resp['point']['geometry']['coordinates']


def extract_exif(img):
    """ Attempt to extact created_at, lon, and lat from the exif tags """
    if img._getexif() is None:
        return None, None, None
    exif = {
        PIL.ExifTags.TAGS[k]: v
        for k, v in img._getexif().items()
        if k in PIL.ExifTags.TAGS
    }

    def _clean_date(exif):
        edt = exif.split(' ')
        edt[0] = edt[0].replace(':', '-')
        return ' '.join(edt)
    lon, lat = None, None
    try:
        dt = parser.parse(_clean_date(exif['DateTime']))
    except ValueError as e:
        dt = parser.parse(_clean_date(exif['DateTimeOriginal']))

    has_fields = False
    if 'GPSInfo' in exif:
        gps = {
            PIL.ExifTags.GPSTAGS[k]: v
            for k, v in exif['GPSInfo'].items()
            if k in PIL.ExifTags.GPSTAGS
        }
        req_fields = ['GPSLongitude', 'GPSLatitude',
                      'GPSLongitudeRef', 'GPSLatitudeRef']
        has_fields = all([field in gps for field in req_fields])
    lon, lat = None, None
    if has_fields:
        # attempt to parse
        lon, lat = parse_gps(gps)

    return dt, lon, lat


@celery.task()
def extract(iid):
    """
    Extracts metadata from an image file
    """
    m = Image.query.get(iid)
    path = os.path.join(current_app.config['IMAGE_UPLOAD_DIR'], m.basepath)

    img = PIL.Image.open(path)
    dt, lon, lat = extract_exif(img)
    img = image_transpose_exif(img)
    # save out the transposed image so that we can correctly read the dims
    img.save(path)
    width, height = img.size
    m.width = width
    m.height = height
    if dt is not None:
        m.created_at = dt

    if lon is None and lat is None and dt is not None:
        # have geo try to interpolate based on the timestamp
        point = interp_point(m.username, m.trip_id, dt)
        if point is not None:
            lon, lat = point[0], point[1]
    if lon is not None and lat is not None:
        m.lon = lon
        m.lat = lat
    db.session.add(m)
    db.session.commit()

    return iid
