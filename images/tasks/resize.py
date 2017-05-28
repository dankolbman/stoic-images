import os
from flask import current_app
from sqlalchemy.orm.attributes import flag_modified
import PIL.Image
from . import celery
from ..model import Image
from images import create_celery_app
from .. import db


@celery.task()
def resize(iid):
    """
    Resize a raw photo into many formats

    i - icon, square
    t - thumbnail, preserve aspect
    f - full, preserve aspect
    64x64       - 64 square thumb
    128x128     - 128 square thumb
    180h        - 180 ht thumb
    256h        - 256 ht thumb
    512x320     - 512x320 image
    1024x640    - 1024x640 image
    """
    sizes = [(64, 64), (128, 128), (180, 0), (256, 0), (512, 320), (1024, 640)]
    m = Image.query.get(iid)
    path = os.path.join(current_app.config['IMAGE_UPLOAD_DIR'], m.basepath)
    img = PIL.Image.open(path)

    paths = {}
    for size in sizes:
        filepath, filename = os.path.split(path)
        tag = size_tag(size)
        filename = filename.replace('.', '_' + tag + '.')
        outpath = os.path.join(filepath, filename)
        cropped = scale_crop(img, size)
        cropped.save(outpath)
        paths[tag] = outpath
    m.paths = paths
    flag_modified(m, "paths")
    db.session.commit()


def size_tag(size):
    """ Generates the appendix for the file name """
    orient = ''
    dims = ''
    if size[0] and not size[1]:
        orient = 'w'
        dims = str(size[0])
    elif not size[0] and size[1]:
        orient = 'h'
        dims = str(size[1])
    elif size[0] and size[1]:
        dims = '{}x{}'.format(size[0], size[1])
    return dims + orient


def scale_crop(img, size, how='auto'):
    """
    Will scale and crop the image down to the appropriate size
    how:
      auto - will resolve to one of the below
      width - preserve ratio and fit given width
      height - preserve ratio and fit given height
      crop - scale and crop to size preserving ratio and not leaving any empty
    """
    if how == 'auto':
        if size[1] is 0:
            how = 'width'
        elif size[0] is 0:
            how = 'height'
        else:
            how = 'crop'
    if how is 'crop':
        img_ratio = img.size[0] / img.size[1]
        ratio = size[0] / size[1]
        wider = img_ratio > ratio

    if how is 'width' or (how is 'crop' and not wider):
        img = img.resize((size[0], int(size[0] * img.size[1] / img.size[0])))
    elif how is 'height'or (how is 'crop' and wider):
        img = img.resize((int(size[1] * img.size[0] / img.size[1]), size[1]))
    if how is 'crop':
        if wider:
            box = (round((img.size[0] - size[0]) / 2), 0,
                   round((img.size[0] + size[0]) / 2), img.size[1])
        elif not wider:
            box = (0, round((img.size[1] - size[1]) / 2), img.size[0],
                   round((img.size[1] + size[1]) / 2))
        img = img.crop(box)

    return img
