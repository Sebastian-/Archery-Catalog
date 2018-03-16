import time
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database_setup import Base, Catalog, Item, Riser, Arrow, Limb, Plunger,\
    Sight

engine = create_engine('sqlite:///archery_catalog.db')
Base.metadata.bind = engine
DBSession = sessionmaker(bind=engine)
session = DBSession()

catalog = Catalog(name="Archery Catalog")
session.add(catalog)
session.commit

c_id = session.query(Catalog).one().id

# Risers
riser1 = Riser(name="MK Archery MK Z", color="White", length="25 Inches",
               handedness="Right Handed", made_of="Aluminum", catalog_id=c_id,
               catalog=catalog)
session.add(riser1)
session.commit()
time.sleep(1)

riser2 = Riser(name="Hoyt Formula Faktor", color="Green", length="27 Inches",
               handedness="Right Handed", made_of="Aluminum", catalog_id=c_id,
               catalog=catalog)
session.add(riser2)
session.commit()
time.sleep(1)

riser3 = Riser(name="Win & Win WIAWIS NANO TFT", color="Black",
               length="25 Inches", handedness="Left Handed", made_of="Carbon",
               catalog_id=c_id, catalog=catalog)
session.add(riser3)
session.commit()
time.sleep(1)

riser4 = Riser(name="Samick Sage Takedown Recurve", color="Brown", 
               length="25 Inches", handedness="Right Handed", 
               made_of="Dymondwood", catalog_id=c_id, catalog=catalog)
session.add(riser4)
session.commit()
time.sleep(1)

# Limbs
limb1 = Limb(name="MK Inpers", catalog_id=c_id, draw_weight="36 lb",
             length="Medium", made_of="Wood/Carbon", catalog=catalog)
session.add(limb1)
session.commit()
time.sleep(1)