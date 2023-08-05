from werkzeug.wrappers import Response
from werkzeug.exceptions import NotFound, BadRequest

import logging
import os

logger = logging.getLogger(__name__)


class CollectionEndpoint(object):

    def GET(self, request):

        return Response([])

    def POST(self, request):

        data = request.content

        return Response({})


class InstanceEndpoint(object):

    def GET(self, request, db_id):

        return Response({})

    def POST(self, request, db_id):

        data = request.content

        return Response({})

    PUT = POST

    def DELETE(self, request, db_id):

        return Response()
