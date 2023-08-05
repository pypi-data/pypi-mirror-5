from sqlalchemy import create_engine
from functools import wraps

engine = create_engine('sqlite:////home/{{TEMPLATE_USER}}/{{TEMPLATE_NAME}}.db')


def transaction(f):
    """Wraps a function call in a SQL transaction.

    This decorator creates a cursor to a database and begins a transaction.
    The cursor is passed to the wrapped function as the keyword argument `db`.

    If the function raises any exceptions, the transaction is rolled back.

    The cursor is closed at the end of the transaction.
    """

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
