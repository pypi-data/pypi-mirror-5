import uuid
from datetime import datetime

from schema import {{TEMPLATE_NAME}}
from services.connection import transaction


class {{TEMPLATE_MODEL}}(object):

    def __init__(self,
                 name,
                 id=None,
                 created=None,
                 modified=None):

        self.id = id
        self.name = name

        if isinstance(created, basestring):
            created = datetime.strptime(created, "%Y-%m-%d %H:%M:%S")
        self.created = created

        if isinstance(modified, basestring):
            modified = datetime.strptime(modified, "%Y-%m-%d %H:%M:%S")
        self.modified = modified

    @transaction
    def save(self, db):

        if self.id is None:

            self._create(db)

            return True

        self._update(db)

        return True

    def _create(self, db):

        self.id = str(uuid.uuid4())
        self.created = self.modified = datetime.now()

        statement = {{TEMPLATE_NAME}}.insert().values(id=self.id,
                                          name=self.name,
                                          created=self.created,
                                          modified=self.modified
                                          )

        result = db.execute(statement)

        self.id = result.inserted_primary_key[0]

    def _update(self, db):

        self.modified = datetime.now()

        statement = ({{TEMPLATE_NAME}}.
                     update().
                     values(name=self.name,
                            modified=self.modified).
                     where({{TEMPLATE_NAME}}.c.id == self.id))

        db.execute(statement)

    @transaction
    def delete(self, db):

        if not hasattr(self, "id"):

            return False

        # Existing {{TEMPLATE_NAME}} object.
        statement = {{TEMPLATE_NAME}}.delete().where({{TEMPLATE_NAME}}.c.id == self.id)

        db.execute(statement)

        return True

    @classmethod
    @transaction
    def load(cls, id, db):

        statement = {{TEMPLATE_NAME}}.select().where({{TEMPLATE_NAME}}.c.id == id)

        result = db.execute(statement).fetchone()

        if not result:

            return None

        # Return new {{TEMPLATE_MODEL}}
        return {{TEMPLATE_MODEL}}(name=result.name,
                    id=result.id,
                    created=result.created,
                    modified=result.modified)

    @classmethod
    @transaction
    def load_all(cls, db):

        statement = {{TEMPLATE_NAME}}.select()

        results = db.execute(statement)

        return [{{TEMPLATE_MODEL}}(name=result.name,
                     id=result.id,
                     created=result.created,
                     modified=result.modified)
                for result in results
                ]

    def to_dict(self):

        return {
            "name": self.name,
            "id": self.id,
            "created": self.created.strftime("%Y-%m-%d %H:%M:%S"),
            "modified": self.modified.strftime("%Y-%m-%d %H:%M:%S")
        }
