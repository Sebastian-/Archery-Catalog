import time
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database_setup import Base, Item, Riser, Arrow, Limb, Plunger,\
    Sight, User

engine = create_engine('sqlite:///archery_catalog.db')
Base.metadata.bind = engine
DBSession = sessionmaker(bind=engine)
session = DBSession()


admin = User(name="Admin", email="sebastian@hsmdev.com",
             picture="http://hsmdev.com/img/archery_catalog300px.png")
session.add(admin)
session.commit()


# Risers
riser1 = Riser(name="MK Archery MK Z", color="White", length="25 Inches",
               handedness="Right Handed", made_of="Aluminum", user_id=1)
session.add(riser1)
session.commit()
time.sleep(1)

riser2 = Riser(name="Hoyt Formula Faktor", color="Green", length="27 Inches",
               handedness="Right Handed", made_of="Aluminum", user_id=1)
session.add(riser2)
session.commit()
time.sleep(1)

riser3 = Riser(name="Win & Win WIAWIS NANO TFT", color="Black",
               length="25 Inches", handedness="Left Handed", made_of="Carbon",
               user_id=1)
session.add(riser3)
session.commit()
time.sleep(1)


# Arrows
arrow1 = Arrow(name="Easton X10", user_id=1, spine="350", length="32 Inches",
               made_of="Carbon/Aluminum", point_weight="100 Grains")
session.add(arrow1)
session.commit()
time.sleep(1)

arrow2 = Arrow(name="Easton Carbon One", user_id=1, spine="550",
               length="30 Inches", made_of="Carbon",
               point_weight="110 Grains")
session.add(arrow2)
session.commit()
time.sleep(1)

arrow3 = Arrow(name="Carbon Express Nano-XR", user_id=1, spine="400",
               length="28 Inches", made_of="Carbon", point_weight="120 Grains")
session.add(arrow3)
session.commit()
time.sleep(1)


# Limbs
limb1 = Limb(name="MK Inpers", draw_weight="36 lb", length="Medium",
             made_of="Wood/Carbon", user_id=1)
session.add(limb1)
session.commit()
time.sleep(1)

limb2 = Limb(name="Uukha XX", draw_weight="40 lb", length="Long",
             made_of="Carbon", user_id=1)
session.add(limb2)
session.commit()
time.sleep(1)

limb3 = Limb(name="Hoyt Grand Prix", draw_weight="32 lb", length="Short",
             made_of="Carbon/Bamboo", user_id=1)
session.add(limb3)
session.commit()
time.sleep(1)


# Plungers
plunger1 = Plunger(name="Beiter Plunger", user_id=1, color="Black")
session.add(plunger1)
session.commit()
time.sleep(1)

plunger2 = Plunger(name="AAE Gold Micro Plunger", user_id=1, color="Red")
session.add(plunger2)
session.commit()
time.sleep(1)

plunger3 = Plunger(name="Shibuya DX Plunger", user_id=1, color="Blue")
session.add(plunger3)
session.commit()
time.sleep(1)


# Sights
sight1 = Sight(name="Shibuya Ultima II RC", user_id=1,
               handedness="Right Handed")
session.add(sight1)
session.commit()
time.sleep(1)

sight2 = Sight(name="Win&Win WS700", user_id=1, handedness="Left Handed")
session.add(sight2)
session.commit()
time.sleep(1)

sight3 = Sight(name="Axcel AX4500", user_id=1, handedness="Right Handed")
session.add(sight3)
session.commit()
time.sleep(1)
