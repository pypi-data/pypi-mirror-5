from werkzeug.serving import run_simple
from application import application


run_simple('localhost', 8080, application)
