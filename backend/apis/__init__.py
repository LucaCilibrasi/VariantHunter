from flask import Blueprint
from flask_restplus import Api

from .automatic_analysis import api as automatic_analysis

enable_doc = True

api_blueprint = Blueprint('api', __name__)

if enable_doc:
    api = Api(title='UFL API', version='1.0', description='TODO', )
else:
    api = Api(title='UFL API', version='1.0', description='TODO', doc=False)


api.init_app(api_blueprint, add_specs=enable_doc)

api.add_namespace(automatic_analysis)
