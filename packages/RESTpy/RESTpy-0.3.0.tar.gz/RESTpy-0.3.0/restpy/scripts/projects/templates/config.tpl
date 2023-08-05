from restpy.wsgi import ExceptionHandlerMiddleware
from restpy.wsgi import SerializationMiddleware
from restpy.wsgi import RequestMiddleware

from restpy.hooks import unique_request
from restpy.hooks import deserialize_request
from restpy.hooks import serialize_response

import logging

# WSGI Middlewares are applied from top to bottom.
# The bottom-most middleware will see the request first and last.
middlewares = [ExceptionHandlerMiddleware,
               UniqueEnvironMiddleware,
               ResponderMiddleware]

# Hooks are applied in the order they are given.
pre_hooks = [unique_request, deserialize_request]
post_hooks = [serialize_response]

# Log configuration for python `logger` calls made during a service request.
log_file_path = "/home/{{TEMPLATE_USER}}/{{TEMPLATE_NAME}}.log"
log_format = ('{"time": "%(asctime)s",'
              '"level": "%(levelname)s",'
              '"logger": "%(name)s",'
              '"path": "%(pathname)s",'
              '"module": "%(module)s",'
              '"function": "%(funcName)s",'
              '"line": %(lineno)d,'
              '"message": "%(message)s"}')

logging.basicConfig(format=log_format,
                    filename=log_file_path,
                    level=logging.DEBUG)
