from flask import Flask
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database_setup import Base, Catalog, Item, Riser

app = Flask(__name__)

engine = create_engine('sqlite:///archery_catalog.db')
Base.metadata.bind = engine
DBSession = sessionmaker(bind=engine)
session = DBSession()

@app.route('/')
def HomePage():
	risers = session.query(Riser).all()
	output = ""
	for r in risers:
		output += r.name
		output += "<br>"
		output += r.type
		output += "<br>"
	return output

if __name__ == '__main__':
	app.debug = True
	app.run(host = '0.0.0.0', port = 5000)