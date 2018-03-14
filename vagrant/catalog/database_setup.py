from sqlalchemy import Column, ForeignKey, Integer, \
    String, DateTime, create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, with_polymorphic
from sqlalchemy.sql import func


Base = declarative_base()


class Catalog(Base):
    __tablename__ = 'catalog'
    id = Column(Integer, primary_key=True)
    name = Column(String(250))

    items = relationship(
        "Item",
        back_populates='catalog',
        cascade='all, delete-orphan')


class Item(Base):
    __tablename__ = 'item'
    id = Column(Integer, primary_key=True)
    catalog_id = Column(ForeignKey('catalog.id'))
    time_created = Column(DateTime(timezone=True), server_default=func.now())
    name = Column(String(250), nullable=False)
    type = Column(String(50))
    # TODO: add user id column?

    catalog = relationship("Catalog", back_populates="items")

    __mapper_args__ = {
        'polymorphic_identity': 'item',
        'polymorphic_on': type
    }


class Riser(Item):
    __tablename__ = 'Riser'
    id = Column(ForeignKey('item.id'), primary_key=True)
    color = Column(String(50), nullable=False)
    length = Column(String(50), nullable=False)
    handedness = Column(String(50), nullable=False)
    made_of = Column(String(250), nullable=False)

    __mapper_args__ = {
        'polymorphic_identity': 'Riser',
    }


class Arrow(Item):
    __tablename__ = 'Arrow'
    id = Column(ForeignKey('item.id'), primary_key=True)
    spine = Column(String(50), nullable=False)
    length = Column(String(50), nullable=False)
    made_of = Column(String(250), nullable=False)

    __mapper_args__ = {
        'polymorphic_identity': 'Arrow',
    }


class Limb(Item):
    __tablename__ = 'Limb'
    id = Column(ForeignKey('item.id'), primary_key=True)
    draw_weight = Column(String(50), nullable=False)
    length = Column(String(50), nullable=False)
    made_of = Column(String(250), nullable=False)

    __mapper_args__ = {
        'polymorphic_identity': 'Limb',
    }


class Plunger(Item):
    __tablename__ = 'Plunger'
    id = Column(ForeignKey('item.id'), primary_key=True)
    color = Column(String(50), nullable=False)

    __mapper_args__ = {
        'polymorphic_identity': 'Plunger',
    }


class Sight(Item):
    __tablename__ = 'Sight'
    id = Column(ForeignKey('item.id'), primary_key=True)
    handedness = Column(String(50), nullable=False)

    __mapper_args__ = {
        'polymorphic_identity': 'Sight',
    }


engine = create_engine('sqlite:///archery_catalog.db')


Base.metadata.create_all(engine)