from werkzeug.wrappers import Response
from werkzeug.exceptions import MethodNotAllowed


class {{TEMPLATE_ENDPOINT}}Endpoint(object):

    def GET(self, request):

        raise MethodNotAllowed()

    def POST(self, request):

        raise MethodNotAllowed()

    def PUT(self, request):

        raise MethodNotAllowed()

    def DELETE(self, request):

        raise MethodNotAllowed()
