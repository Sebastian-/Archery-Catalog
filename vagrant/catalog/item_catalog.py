from flask import Flask, url_for, render_template
from sqlalchemy import create_engine, desc, distinct, inspect
from sqlalchemy.orm import sessionmaker
from database_setup import Base, Catalog, Item, Riser, Limb
import collections

app = Flask(__name__)

engine = create_engine('sqlite:///archery_catalog.db')
Base.metadata.bind = engine
DBSession = sessionmaker(bind=engine)
session = DBSession()

@app.route("/")
def homePage():
	# These queries assume there is only one catalog in the database
	recent_items = session.query(Item).order_by(desc(Item.time_created)).limit(10)
	categories = session.query(Item.type).distinct()
	output = "RECENT ITEMS <br>"
	for r in recent_items:
		output += "<a href="+url_for("itemPage", item_type=r.type, item_id=r.id)+">"
		output += r.name
		output += "<br>"
		output += str(r.time_created)
		output += "<br>"
		output += "</a><br>"
	output += "CATEGORIES <br>"
	for c in categories:
		output += "<a href="+url_for("categoryPage", item_type=c.type)+">"
		output += "<br>"
		output += c.type
		output += "</a><br>"
	return output


@app.route("/<item_type>/")
def categoryPage(item_type):
	items = session.query(Item).filter(Item.type == item_type)
	output = ""
	for i in items:
		output += "<a href=\""+url_for("itemPage", item_type=i.type, item_id=i.id)+"\" /a>"
		output += "<br>"
		output += i.name
		output += "<br>"
	return output


@app.route("/<item_type>/<int:item_id>/")
def itemPage(item_type, item_id):
	item = session.query(Item).filter(Item.id == item_id).one()
	mapper = inspect(item)
	output = ""
	for col in mapper.attrs:
		output += col.key + " : " + str(col.value)
		output += "<br>"
	output += "<a href="+url_for("editItem", item_type=item.type, item_id=item.id)+">"
	output += "Edit"
	output += "</a><br>"
	return output


@app.route("/<item_type>/<int:item_id>/edit/")
def editItem(item_type, item_id):
	item = session.query(Item).filter(Item.id == item_id).one()
	fields = getDisplayDict(item)
	return render_template("edit_item.html", fields=fields, item=item)


def getDisplayDict(item):
	"""Returns a dictionary containing the user-facing fields of an item.
	Field names are formatted so that they contain no underscores and have
	the first letter of each word capitalized."""
	private_fields = ["id", "catalog_id", "time_created", "type", "catalog"]
	d = collections.OrderedDict()
	mapper = inspect(item)
	for col in mapper.attrs:
		if col.key not in private_fields:
			key = str(col.key).replace("_"," ").title()
			d[key] = str(col.value)
	return d


if __name__ == '__main__':
	app.debug = True
	app.run(host = '0.0.0.0', port = 8000)