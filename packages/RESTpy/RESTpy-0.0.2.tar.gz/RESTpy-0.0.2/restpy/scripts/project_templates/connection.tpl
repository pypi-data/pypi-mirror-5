from sqlalchemy import create_engine
from functools import wraps

engine = create_engine('sqlite:////home/{{TEMPLATE_USER}}/{{TEMPLATE_NAME}}.db')


def transaction(f):

    @wraps(f)
    def wrapper(*args, **kwargs):

        db_connection = engine.connect()
        db_transaction = db_connection.begin()

        kwargs['db'] = db_connection

        try:
            results = f(*args, **kwargs)
            db_transaction.commit()
            db_connection.close()
            return results
        except Exception as e:

            db_transaction.rollback()
            db_connection.close()
            raise e

    return wrapper
