from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database_setup import Base, Catalog, Item, Riser, Arrow, Limb, Plunger,\
    Sight

engine = create_engine('sqlite:///archery_catalog.db')
Base.metadata.bind = engine
DBSession = sessionmaker(bind=engine)
session = DBSession()


catalog = Catalog(name="Archery Catalog")

# Risers
riser1 = Riser(name="MK Archery MK Z", color="White", length="25 Inches",
               handedness="Right Handed", made_of="Aluminum")
catalog.items.append(riser1)

riser2 = Riser(name="Hoyt Formula Faktor", color="Green", length="27 Inches",
               handedness="Right Handed", made_of="Aluminum")
catalog.items.append(riser2)

riser3 = Riser(name="Win & Win WIAWIS NANO TFT", color="Black",
               length="25 Inches", handedness="Left Handed", made_of="Carbon")
catalog.items.append(riser3)

riser4 = Riser(name="Samick Sage Takedown Recurve", color="Brown", 
               length="25 Inches", handedness="Right Handed", 
               made_of="Dymondwood")
catalog.items.append(riser4)


session.add(catalog)
session.commit()
