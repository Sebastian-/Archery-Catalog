from sqlalchemy import Column, ForeignKey, Integer, \
    String, DateTime, create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, with_polymorphic
from sqlalchemy.sql import func


Base = declarative_base()


class User(Base):
    __tablename__ = "user"

    id = Column(Integer, primary_key=True)
    name = Column(String(250), nullable=False)
    email = Column(String(250), nullable=False)
    picture = Column(String(500))
    items = relationship("Item", back_populates="user")


class Item(Base):
    __tablename__ = 'item'

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('user.id'))
    time_created = Column(DateTime(timezone=True), server_default=func.now())
    name = Column(String(250), nullable=False)
    type = Column(String(50))

    user = relationship("User", back_populates="items")

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

    @property
    def serialize(self):
        return {
            "type": self.type,
            "name": self.name,
            "color": self.color,
            "length": self.length,
            "handedness": self.handedness,
            "made_of": self.made_of,
        }


class Arrow(Item):
    __tablename__ = 'Arrow'

    id = Column(ForeignKey('item.id'), primary_key=True)
    spine = Column(String(50), nullable=False)
    length = Column(String(50), nullable=False)
    made_of = Column(String(250), nullable=False)
    point_weight = Column(String(50), nullable=False)

    __mapper_args__ = {
        'polymorphic_identity': 'Arrow',
    }

    @property
    def serialize(self):
        return {
            "type": self.type,
            "name": self.name,
            "spine": self.spine,
            "length": self.length,
            "made of": self.made_of,
            "point_weight": self.point_weight,
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

    @property
    def serialize(self):
        return {
            "type": self.type,
            "name": self.name,
            "draw_weight": self.draw_weight,
            "length": self.length,
            "made_of": self.made_of,
        }


class Plunger(Item):
    __tablename__ = 'Plunger'

    id = Column(ForeignKey('item.id'), primary_key=True)
    color = Column(String(50), nullable=False)

    __mapper_args__ = {
        'polymorphic_identity': 'Plunger',
    }

    @property
    def serialize(self):
        return {
            "type": self.type,
            "name": self.name,
            "color": self.color,
        }


class Sight(Item):
    __tablename__ = 'Sight'

    id = Column(ForeignKey('item.id'), primary_key=True)
    handedness = Column(String(50), nullable=False)

    __mapper_args__ = {
        'polymorphic_identity': 'Sight',
    }

    @property
    def serialize(self):
        return {
            "type": self.type,
            "name": self.name,
            "handedness": self.handedness,
        }


engine = create_engine('sqlite:///archery_catalog.db')


Base.metadata.create_all(engine)
