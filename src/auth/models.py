from datetime import datetime

from sqlalchemy import MetaData, Table, Column, Integer, String, TIMESTAMP, ForeignKey, Boolean, Sequence

metadata = MetaData()

role = Table(
    'role',
    metadata,
    Column('id', Integer, primary_key=True),
    Column('type', String, nullable=False)
)

user = Table(
    'user',
    metadata,
    Column('id', Integer, Sequence('user_id_seq'), primary_key=True, autoincrement=True),
    Column('email', String, nullable=False),
    Column('username', String, nullable=False),
    Column('hashed_password', String, nullable=False),
    Column('registered_at', TIMESTAMP, default=datetime.now()),
    Column('role_id', Integer, ForeignKey(role.c.id)),
    Column('is_superuser', Boolean, default=True, nullable=False),
    Column('is_active', Boolean, default=True, nullable=False),
    Column('is_verified', Boolean, default=False, nullable=False),
)



