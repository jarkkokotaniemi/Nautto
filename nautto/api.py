
from nautto.resources.user import UserCollection, UserItem
from nautto.resources.widget import WidgetsByUserCollection, WidgetCollection, WidgetItem
from nautto.resources.layout import LayoutsByUserCollection, LayoutCollection, LayoutItem
from flask import Blueprint
from flask_restful import Api

api_bp = Blueprint("api", __name__, url_prefix="/api")
api = Api(api_bp)

api.add_resource(UserCollection, "/users/")
api.add_resource(UserItem, "/users/<user>/")

api.add_resource(WidgetsByUserCollection, "/users/<user>/widgets/")
api.add_resource(WidgetCollection, "/widgets/")
api.add_resource(WidgetItem, "/widgets/<widget>/")

api.add_resource(LayoutsByUserCollection, "/users/<user>/layouts/")
api.add_resource(LayoutCollection, "/layouts/")
api.add_resource(LayoutItem, "/layouts/<layout>/")
