from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

from sqlalchemy import (
    Column,
    Integer,
    String,
    ForeignKey,
    Table
)

Base = declarative_base()

tag_post = Table('tag_post', Base.metadata,
                 Column('post_id', Integer, ForeignKey('post.id')),
                 Column('tag_id', Integer, ForeignKey('tag.id'))
                 )

hub_post = Table('hub_post', Base.metadata,
                 Column('post_id', Integer, ForeignKey('post.id')),
                 Column('hub_id', Integer, ForeignKey('hub.id'))
                 )


class Post(Base):
    __tablename__ = 'post'
    id = Column(Integer, primary_key=True, autoincrement=True)
    title = Column(String, unique=False, nullable=False)
    url = Column(String, unique=True, nullable=False)
    writer_id = Column(Integer, ForeignKey('writer.id'))
    writer = relationship("Writer", back_populates='post')
    tag = relationship('Tag', secondary=tag_post, back_populates='post')
    hub = relationship('hub', secondary=hub_post, back_populates='post')

    def __init__(self, title: str, url: str, writer_id, tags: list = None, hubs: list = None):
        self.title = title
        self.url = url
        self.writer_id = writer_id
        if tags:
            self.tag.extend(tags)
        if hubs:
            self.hub.extend(hubs)

class Writer(Base):
    __tablename__ = 'writer'
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String, unique=False, nullable=False)
    username = Column(String, unique=True, nullable=False)
    url = Column(String, unique=True, nullable=False)
    post = relationship("Post", back_populates='writer')

    def __init__(self, name: str, url: str, username: str):
        self.name = name
        self.url = url
        self.username = username



class Tag(Base):
    __tablename__ = 'tag'
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String, unique=False, nullable=False)
    url = Column(String, unique=True, nullable=False)
    post = relationship('Post', secondary=tag_post, back_populates='tag')

    def __init__(self, name: str, url: str):
        self.name = name
        self.url = url

class Hub(Base):
    __tablename__ = 'hub'
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String, unique=False)
    url = Column(String, unique=True, nullable=False)
    post = relationship('Post', secondary=hub_post, back_populates='hub')


    def __init__(self, name: str, url: str):
        self.name = name
        self.url = url
