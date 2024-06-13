from sqlalchemy import Table, Column, Integer, String, TIMESTAMP, MetaData, ForeignKey
from datetime import datetime

metadata = MetaData()

Categories = Table(
    'categories',
    metadata,
    Column('id', Integer, primary_key=True),
    Column('type', String, nullable=False)
)

Manga = Table(
    'manga',
    metadata,
    Column('id', Integer, primary_key=True),
    Column('author', String, nullable=False),
    Column('head', String, nullable=False),
    Column('about', String, nullable=False),
    Column('path_to_manga', String, nullable=False),
    Column('categories', Integer, ForeignKey(Categories.c.id)),
    Column('chapter', Integer, nullable=False),
    Column('created_at', TIMESTAMP, default=datetime.now())
)