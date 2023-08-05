"""This module is the root service for all REST service nodes."""

from restpy.applications import RestApplication

from config import middlewares, pre_hooks, post_hooks

from urls import routes

# This is name of the exported WSGI application that can served:
application = RestApplication(routes, pre_hooks, post_hooks)

# Wrap the base application in user defined middlewares.
for middleware in middlewares:

    application = middleware(application)
