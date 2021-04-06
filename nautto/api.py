
from nautto.resources.user import UserCollection, UserItem
from flask import Blueprint
from flask_restful import Api

api_bp = Blueprint("api", __name__, url_prefix="/api")
api = Api(api_bp)

api.add_resource(UserCollection, "/users/")
api.add_resource(UserItem, "/users/<user>/")
