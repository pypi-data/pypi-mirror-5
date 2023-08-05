from restpy.wsgi import ExceptionHandlerMiddleware
from restpy.wsgi import SerializationMiddleware
from restpy.wsgi import RequestMiddleware

import logging

# WSGI Middlewares are applied from left to right.
# The right-most middleware will see the request first and last.
middlewares = [ExceptionHandlerMiddleware,
               SerializationMiddleware,
               RequestMiddleware]

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
