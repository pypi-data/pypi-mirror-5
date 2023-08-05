from werkzeug.wrappers import Response
from werkzeug.exceptions import NotFound, BadRequest

import logging
import os

from models import {{TEMPLATE_MODEL}}

logger = logging.getLogger(__name__)


class CollectionEndpoint(object):

    def GET(self, request):

        return Response([r.to_dict() for r in {{TEMPLATE_MODEL}}.load_all()])

    def POST(self, request):

        data = request.content

        try:
            assert "name" in data
            assert isinstance(data["name"], basestring)
        except:
            raise BadRequest("{{TEMPLATE_MODEL}} must have a `name` attribute "
                             "with a type of string.")

        r = {{TEMPLATE_MODEL}}(name=data["name"])

        r.save()

        r.path = os.path.join(root_path, r.db_id)

        r.save()

        return Response(r.to_dict())


class InstanceEndpoint(object):

    def GET(self, request, db_id):

        r = {{TEMPLATE_MODEL}}.load(db_id)

        if r is None:

            raise NotFound("{{TEMPLATE_MODEL}} with id %s could not be found." % db_id)

        return Response(r.to_dict())

    def POST(self, request, db_id):

        data = request.content

        try:
            assert "name" in data
            assert isinstance(data["name"], basestring)
        except:
            raise BadRequest("{{TEMPLATE_MODEL}} must have a `name` attribute "
                             "with a type of string.")

        r = {{TEMPLATE_MODEL}}.load(db_id)

        if r is None:

            raise NotFound("{{TEMPLATE_MODEL}} with id %s could not be found." % db_id)

        r.name = data['name']

        r.save()

        return Response(r.to_dict())

    PUT = POST

    def DELETE(self, request, db_id):

        r = {{TEMPLATE_MODEL}}.load(db_id)

        if r is None:

            raise NotFound("{{TEMPLATE_MODEL}} with id %s could not be found." % db_id)

        r.delete()

        return Response()
