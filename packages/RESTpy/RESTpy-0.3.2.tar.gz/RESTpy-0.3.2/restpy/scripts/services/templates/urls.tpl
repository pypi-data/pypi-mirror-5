from werkzeug.routing import Rule

from endpoints import CollectionEndpoint, InstanceEndpoint

urls = [
    Rule('/{{TEMPLATE_NAME}}/', endpoint=CollectionEndpoint),
    Rule('/{{TEMPLATE_NAME}}/<uuid:id>/', endpoint=InstanceEndpoint)
]
