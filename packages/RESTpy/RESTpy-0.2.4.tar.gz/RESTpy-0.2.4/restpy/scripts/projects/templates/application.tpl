"""This module is the root service for all REST service nodes."""

from restpy.applications import RestApplication

from config import middlewares

from urls import routes

# This is name of the exported WSGI application that can served:
application = RestApplication(routes)

# Wrap the base application in user defined middlewares.
for middleware in middlewares:

    application = middleware(application)
