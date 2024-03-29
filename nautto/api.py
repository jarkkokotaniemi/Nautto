
from nautto.resources.user import UserCollection, UserItem
from nautto.resources.widget import WidgetsByUserCollection, WidgetCollection, WidgetItem, WidgetOfLayout
from nautto.resources.layout import LayoutsByUserCollection, LayoutCollection, LayoutItem, LayoutOfSet
from nautto.resources.set import SetsByUserCollection, SetCollection, SetItem
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
api.add_resource(WidgetOfLayout, "/layouts/<layout>/widgets/<widget>/")

api.add_resource(SetsByUserCollection, "/users/<user>/sets/")
api.add_resource(SetCollection, "/sets/")
api.add_resource(SetItem, "/sets/<set>/")
api.add_resource(LayoutOfSet, "/sets/<set>/layouts/<layout>/")