from images import create_celery_app

celery = create_celery_app()

# Need to have these after celery to avoid circular deps
from .resize import resize  # noqa
from config import config  # noqa
