from flask import Flask, url_for
from sqlalchemy import create_engine, desc, distinct, inspect
from sqlalchemy.orm import sessionmaker
from database_setup import Base, Catalog, Item, Riser, Limb

app = Flask(__name__)

engine = create_engine('sqlite:///archery_catalog.db')
Base.metadata.bind = engine
DBSession = sessionmaker(bind=engine)
session = DBSession()

@app.route("/")
def HomePage():
	# These queries assume there is only one catalog in the database
	recent_items = session.query(Item).order_by(desc(Item.time_created)).limit(10)
	categories = session.query(Item.type).distinct()
	output = "RECENT ITEMS <br>"
	for r in recent_items:
		output += "<a href="+url_for("ItemPage", item_type=r.type, item_id=r.id)+">"
		# output += "<a href="+url_for(r.type+"Page", item_id=r.id)+">"
		output += r.name
		output += "<br>"
		output += str(r.time_created)
		output += "<br>"
		output += "</a><br>"
	output += "CATEGORIES <br>"
	for c in categories:
		output += "<a href="+url_for("CategoryPage", item_type=c.type)+">"
		output += "<br>"
		output += c.type
		output += "</a><br>"
	return output


@app.route("/<item_type>/<int:item_id>/")
def ItemPage(item_type, item_id):
	item = session.query(Item).filter(Item.type == item_type).filter(Item.id == item_id)[0]
	mapper = inspect(item)
	output = ""
	for col in mapper.attrs:
		if col.value:
			output += col.key + " : " + str(col.value)
			output += "<br>"
	return output


@app.route("/<item_type>/")
def CategoryPage(item_type):
	items = session.query(Item).filter(Item.type == item_type)
	output = ""
	for i in items:
		output += "<a href=\""+url_for("ItemPage", item_type=i.type, item_id=i.id)+"\" /a>"
		output += "<br>"
		output += i.name
		output += "<br>"
	return output


if __name__ == '__main__':
	app.debug = True
	app.run(host = '0.0.0.0', port = 8000)