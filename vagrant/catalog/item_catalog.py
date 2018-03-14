from flask import Flask
from sqlalchemy import create_engine, desc, distinct
from sqlalchemy.orm import sessionmaker
from database_setup import Base, Catalog, Item, Riser

app = Flask(__name__)

engine = create_engine('sqlite:///archery_catalog.db')
Base.metadata.bind = engine
DBSession = sessionmaker(bind=engine)
session = DBSession()

@app.route('/')
def HomePage():
	# This assumes there is only one catalog in the database
	recent_items = session.query(Item).order_by(desc(Item.time_created)).limit(10)
	categories = session.query(Item.type).distinct()
	output = "RECENT ITEMS <br>"
	for r in recent_items:
		output += r.name
		output += "<br>"
		output += str(r.time_created)
		output += "<br>"
	output += "CATEGORIES <br>"
	for c in categories:
		output += c.type
		output += "<br>"

	return output

if __name__ == '__main__':
	app.debug = True
	app.run(host = '0.0.0.0', port = 8000)