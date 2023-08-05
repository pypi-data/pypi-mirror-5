from os import listdir, path

from werkzeug.routing import Rule, Map
from restpy.routing import UuidConverter

from endpoints import {{TEMPLATE_ENDPOINT}}Endpoint

urls = [
    Rule('/', endpoint={{TEMPLATE_ENDPOINT}}Endpoint)
]

# Auto-discover available services and add them to the routing.
for service in (s for s in
                listdir(path.join(path.dirname(__file__), "services"))
                if "." not in s):

    service_urls = __import__("services." + service + ".urls",
                              fromlist=['services'])

    urls += service_urls.urls

routes = Map(urls, converters={'uuid': UuidConverter})
