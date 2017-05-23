from flask_restplus import Api
from .images import api as image_ns

api = Api(
    title='Images',
    version='1.0',
    description='Image processing service',
    contact='Dan Kolbman',
    cantact_url='dankolbman.com',
    contact_email='dan@kolbman.com'
)

api.add_namespace(image_ns)
