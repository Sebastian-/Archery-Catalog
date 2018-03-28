import collections, random, string, json, requests, httplib2

from flask import Flask, url_for, render_template, request, redirect, make_response, flash
from flask import session as login_session
from sqlalchemy import create_engine, desc, distinct, inspect
from sqlalchemy.orm import sessionmaker
from oauth2client.client import flow_from_clientsecrets, FlowExchangeError

from database_setup import Base, Catalog, Item, Riser, Limb, Arrow, Plunger, Sight

app = Flask(__name__)
engine = create_engine('sqlite:///archery_catalog.db')
Base.metadata.bind = engine
DBSession = sessionmaker(bind=engine)
session = DBSession()
CLIENT_ID = json.loads(open("client_secrets.json", "r").read())["web"]["client_id"]


# Queries assume there is only one catalog in the database


@app.route("/")
def homePage():
	recent_items = session.query(Item).order_by(desc(Item.time_created)).limit(10)
	categories = [cls.__name__ for cls in Item.__subclasses__()]
	return render_template("index.html", items=recent_items, categories=categories)


@app.route("/category/<item_type>/")
def categoryPage(item_type):
	items = session.query(Item).filter(Item.type == item_type).order_by(desc(Item.time_created))
	return render_template("category_page.html", items=items, category=item_type)


@app.route("/category/<item_type>/<int:item_id>/")
def itemPage(item_type, item_id):
	item = session.query(Item).filter(Item.id == item_id).first()
	fields = getDisplayDict(item)
	return render_template("item_page.html", item=item, fields=fields)


@app.route("/category/<item_type>/new", methods=["GET", "POST"])
def newItemPage(item_type):
	if "username" not in login_session:
		return redirect(url_for("showLogin"))
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


@app.route("/category/<item_type>/<int:item_id>/edit/", methods=["GET", "POST"])
def editItem(item_type, item_id):
	if "username" not in login_session:
		return redirect(url_for("showLogin"))
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


@app.route("/category/<item_type>/<int:item_id>/delete", methods=["GET", "POST"])
def deleteItemPage(item_type, item_id):
	if "username" not in login_session:
		return redirect(url_for("showLogin"))
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


# CODE PROVIDED BY UDACITY ----------------------------------------------------
# https://github.com/udacity/ud330/blob/master/Lesson2/step6/project.py



@app.route("/login")
def showLogin():
	# Create anti-forgery state token
    state = ''.join(random.choice(string.ascii_uppercase + string.digits)
                    for x in xrange(32))
    login_session['state'] = state
    return render_template("login.html", STATE=state, client_id=CLIENT_ID, return_url=request.referrer)


@app.route('/gconnect', methods=['POST'])
def gconnect():
    # Validate state token
    if request.args.get('state') != login_session['state']:
        response = make_response(json.dumps('Invalid state parameter.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    # Obtain authorization code
    code = request.data

    try:
        # Upgrade the authorization code into a credentials object
        oauth_flow = flow_from_clientsecrets('client_secrets.json', scope='')
        oauth_flow.redirect_uri = 'postmessage'
        credentials = oauth_flow.step2_exchange(code)
    except FlowExchangeError:
        response = make_response(
            json.dumps('Failed to upgrade the authorization code.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Check that the access token is valid.
    access_token = credentials.access_token
    url = ('https://www.googleapis.com/oauth2/v1/tokeninfo?access_token=%s'
           % access_token)
    h = httplib2.Http()
    result = json.loads(h.request(url, 'GET')[1])
    # If there was an error in the access token info, abort.
    if result.get('error') is not None:
        response = make_response(json.dumps(result.get('error')), 500)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Verify that the access token is used for the intended user.
    gplus_id = credentials.id_token['sub']
    if result['user_id'] != gplus_id:
        response = make_response(
            json.dumps("Token's user ID doesn't match given user ID."), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Verify that the access token is valid for this app.
    if result['issued_to'] != CLIENT_ID:
        response = make_response(
            json.dumps("Token's client ID does not match app's."), 401)
        print "Token's client ID does not match app's."
        response.headers['Content-Type'] = 'application/json'
        return response

    stored_access_token = login_session.get('access_token')
    stored_gplus_id = login_session.get('gplus_id')
    if stored_access_token is not None and gplus_id == stored_gplus_id:
        response = make_response(json.dumps('Current user is already connected.'),
                                 200)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Store the access token in the session for later use.
    login_session['access_token'] = credentials.access_token
    login_session['gplus_id'] = gplus_id

    # Get user info
    userinfo_url = "https://www.googleapis.com/oauth2/v1/userinfo"
    params = {'access_token': credentials.access_token, 'alt': 'json'}
    answer = requests.get(userinfo_url, params=params)

    data = answer.json()

    login_session['username'] = data['name']
    login_session['picture'] = data['picture']
    login_session['email'] = data['email']
    
    output = ''
    output += '<h1>Welcome, '
    output += login_session['username']
    output += '!</h1>'
    output += '<img src="'
    output += login_session['picture']
    output += ' " style = "width: 300px; height: 300px;border-radius: 150px;-webkit-border-radius: 150px;-moz-border-radius: 150px;"> '
    flash("you are now logged in as %s" % login_session['username'])
    print "done!"
    return output 


@app.route('/gdisconnect')
def gdisconnect():
    access_token = login_session.get('access_token')
    if access_token is None:
        print 'Access Token is None'
        response = make_response(json.dumps('Current user not connected.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    print 'In gdisconnect access token is %s', access_token
    print 'User name is: '
    print login_session['username']
    url = 'https://accounts.google.com/o/oauth2/revoke?token=%s' % login_session['access_token']
    h = httplib2.Http()
    result = h.request(url, 'GET')[0]
    print 'result is '
    print result
    if result['status'] == '200':
        del login_session['access_token']
        del login_session['gplus_id']
        del login_session['username']
        del login_session['email']
        del login_session['picture']
        response = make_response(json.dumps('Successfully disconnected.'), 200)
        response.headers['Content-Type'] = 'application/json'
        return response
    else:
        response = make_response(json.dumps('Failed to revoke token for given user.', 400))
        response.headers['Content-Type'] = 'application/json'
        return response


# CODE PROVIDED BY UDACITY ----------------------------------------------------
# https://github.com/udacity/ud330/blob/master/Lesson2/step6/project.py


if __name__ == '__main__':
	app.secret_key = "Robin_Hood_was_here"
	app.debug = True
	app.run(host = '0.0.0.0', port = 8000)