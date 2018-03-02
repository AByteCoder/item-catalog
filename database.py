#!/usr/bin/python3

# contains tables needed for the project

from sqlalchemy import create_engine, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, Date, DateTime
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship, sessionmaker

engine = create_engine("sqlite:///catalog.db")
Base = declarative_base()


# users table alongs with its componentes
class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    email = Column(String, nullable=False)
    pic = Column(String, nullable=False)
    created_on = Column(Date, default=func.now())

    @property
    def serialize(self):
        """ serialized version of User"""
        return {
            'id': self.id,
            'name': self.name,
            'email': self.email,
            'pic': self.pic,
            'categories': [category.serialize for category in self.categories],
            'items': [item.serialize for item in self.items]
            }


# categories table alongs with its componentes
class Category(Base):
    __tablename__ = "categories"
    id = Column(Integer, primary_key=True)
    latest_update = Column(DateTime, default=func.now())
    created_by = Column(Integer, ForeignKey('users.id'))
    name = Column(String, nullable=False)
    description = Column(String, nullable=False)
    created_user = relationship("User", back_populates="categories")

    @property
    def serialize(self):
        """ serialized version of Category """
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'last-update': self.latest_update,
            'created_by': {
                            'name': self.created_user.name,
                            'email': self.created_user.email,
                            'pic': self.created_user.pic,
                            'id': self.created_user.id
                            },
            'items': [item.serialize for item in self.items]
            }


# categoryItem table alongs with its componentes
class CategoryItem(Base):
    __tablename__ = "category_items"
    id = Column(Integer, primary_key=True)
    belongs_to = Column(Integer, ForeignKey('categories.id'))
    latest_update = Column(DateTime, default=func.now())
    created_by = Column(Integer, ForeignKey('users.id'))
    name = Column(String, nullable=False)
    description = Column(String, nullable=False)
    created_user = relationship("User", back_populates="items")
    category = relationship("Category", back_populates="items")

    @property
    def serialize(self):
        """ serialized version of category items """
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'last-update': self.latest_update,
            'belongs-to': self.category.id,
            'created_by': {
                            'name': self.created_user.name,
                            'email': self.created_user.email,
                            'pic': self.created_user.pic,
                            'id': self.created_user.id
                            }
            }


User.categories = relationship("Category", back_populates="created_user")
User.items = relationship("CategoryItem", back_populates="created_user")
Category.items = relationship("CategoryItem", back_populates="category",
                              cascade="delete")
Base.metadata.create_all(engine)
Session = sessionmaker(bind=engine)
db_session = Session()
