from . import celery
from ..model import Image
from images import create_celery_app


@celery.task()
def resize(filepath):
    """
    Resize a raw photo into many formats
    """
    pass
