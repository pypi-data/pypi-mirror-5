======
RESTpy
======

**Werkzeug utilites for building RESTful services.**

What is RESTpy?
===============

RESTpy is a small set of utilities built on werkzeug that make it a little
easier to roll out a RESTful web service.

Example Usage
=============

::

    from restpy.applications import RestApplication

    from werkzeug.routing import Map, Rule
    from werkzeug.wrappers import Response


    class IndexEndpoint(object):

        def GET(self, request):
            return Response("GET")

        def POST(self, request):
            return Response("POST")

        def PUT(self, request):
            return Response("PUT")

        def DELETE(self, request):
            return Response("DELETE")

    urls = Map([Rule("/", endpoint=IndexEndpoint)])

    application = RestApplication(urls)

This package also comes with a helper script that can generate RESTful web
service project or individual service handler skeletons::

    $ restpy project create MySocialNetwork
    $ cd MySocialNetwork
    $ restpy service create person
    $ restpy service create friend

License
=======

This project is released under the same BSD license as werkzeug::

    Copyright (c) 2013 by Kevin Conway

    Redistribution and use in source and binary forms, with or without
    modification, are permitted provided that the following conditions are
    met:

        * Redistributions of source code must retain the above copyright
          notice, this list of conditions and the following disclaimer.

        * Redistributions in binary form must reproduce the above
          copyright notice, this list of conditions and the following
          disclaimer in the documentation and/or other materials provided
          with the distribution.

        * The names of the contributors may not be used to endorse or
          promote products derived from this software without specific
          prior written permission.

    THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS
    "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT
    LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR
    A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT
    OWNER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL,
    SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT
    LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE,
    DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY
    THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
    (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
    OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

Contributor's Agreement
=======================

All contributions to this project are protected by the contributors agreement
detailed in the CONTRIBUTING file. All contributors should read the file before
contributing, but as a summary::

    You give us the rights to distribute your code and we promise to maintain
    an open source release of anything you contribute.
