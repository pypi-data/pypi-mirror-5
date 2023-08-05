from werkzeug.serving import run_simple
from application import application

from services import connection

connection.reload_all()

# Run a local development server for basic testing.
run_simple('localhost', 8080, application)
