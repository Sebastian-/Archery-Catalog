import collections

from flask import Flask, url_for, render_template, request, redirect
from sqlalchemy import create_engine, desc, distinct, inspect
from sqlalchemy.orm import sessionmaker

from database_setup import Base, Catalog, Item, Riser, Limb, Arrow, Plunger, Sight

app = Flask(__name__)
engine = create_engine('sqlite:///archery_catalog.db')
Base.metadata.bind = engine
DBSession = sessionmaker(bind=engine)
session = DBSession()


# Queries assume there is only one catalog in the database


@app.route("/")
def homePage():
	recent_items = session.query(Item).order_by(desc(Item.time_created)).limit(10)
	categories = [cls.__name__ for cls in Item.__subclasses__()]
	return render_template("index.html", items=recent_items, categories=categories)


@app.route("/<item_type>/")
def categoryPage(item_type):
	items = session.query(Item).filter(Item.type == item_type).order_by(desc(Item.time_created))
	output = ""
	for i in items:
		output += "<a href="+url_for("itemPage", item_type=i.type, item_id=i.id)+">"
		output += "<br>"
		output += i.name
		output += "</a><br>"
	output += "<br><a href="+url_for("newItemPage", item_type=item_type)+">"
	output += "New"
	output += "</a><br>"
	return output


@app.route("/<item_type>/<int:item_id>/")
def itemPage(item_type, item_id):
	item = session.query(Item).filter(Item.id == item_id).first()
	fields = getDisplayDict(item)
	return render_template("item_page.html", item=item, fields=fields)


@app.route("/<item_type>/new", methods=["GET", "POST"])
def newItemPage(item_type):
	constructor = globals()[item_type]
	new_item = constructor()
	if request.method == "POST":
		for key, value in request.form.items():
			field_name = formatFieldName(key, undo=True)
			setattr(new_item, field_name, value)
		session.add(new_item)
		session.commit()
		return redirect(url_for("categoryPage", item_type=item_type))
	else:
		fields = getDisplayDict(new_item)
		return render_template("new_item.html", fields=fields, item=new_item)


@app.route("/<item_type>/<int:item_id>/edit/", methods=["GET", "POST"])
def editItem(item_type, item_id):
	item = session.query(Item).filter(Item.id == item_id).first()
	if not item:
		return redirect(url_for("categoryPage", item_type=item.type))
	if request.method == "POST":
		for key, value in request.form.items():
			if value:
				field_name = formatFieldName(key, undo=True)
				setattr(item, field_name, value)
		session.add(item)
		session.commit()
		return redirect(url_for("itemPage", item_type=item_type, item_id=item.id))
	else:
		fields = getDisplayDict(item)
		return render_template("edit_item.html", fields=fields, item=item)


@app.route("/<item_type>/<int:item_id>/delete", methods=["GET", "POST"])
def deleteItemPage(item_type, item_id):
	item = session.query(Item).filter(Item.id == item_id).first()
	if not item:
		# This handles the case where a user goes back and clicks cancel after already deleting an item
		return redirect(url_for("categoryPage", item_type=item_type))
	if request.method == "POST":
		session.delete(item)
		session.commit()
		return redirect(url_for("categoryPage", item_type=item_type))
	else:
		return render_template("delete_item.html", item_type=item_type, item=item)


def getDisplayDict(item):
	"""Returns a dictionary containing the user-facing fields of an item.
	Field names are formatted so that they contain no underscores and have
	the first letter of each word capitalized."""
	private_fields = ["id", "catalog_id", "time_created", "type", "catalog"]
	d = collections.OrderedDict()
	mapper = inspect(item)
	for col in mapper.attrs:
		if col.key not in private_fields:
			key = formatFieldName(str(col.key))
			d[key] = str(col.value)
	return d


def formatFieldName(field, undo=False):
	if undo:
		return field.replace(" ","_").lower()
	else:
		return field.replace("_"," ").title()


if __name__ == '__main__':
	app.debug = True
	app.run(host = '0.0.0.0', port = 8000)