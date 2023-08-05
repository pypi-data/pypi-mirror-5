from werkzeug.serving import run_simple
from application import application


# Run a local development server for basic testing.
run_simple('localhost', 8080, application)
