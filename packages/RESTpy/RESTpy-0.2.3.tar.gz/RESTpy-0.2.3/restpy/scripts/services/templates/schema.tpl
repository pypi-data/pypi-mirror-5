from sqlalchemy import MetaData, Table, Column

from sqlalchemy.types import CHAR, NVARCHAR, VARCHAR, BIGINT, DATETIME

metadata = MetaData()

{{TEMPLATE_NAME}} = Table('{{TEMPLATE_NAME}}',
              metadata,
              Column('file_id', CHAR(length=36), primary_key=True),
              Column('name', NVARCHAR(length=255)),
              Column('created', DATETIME),
              Column('modified', DATETIME)
              )
