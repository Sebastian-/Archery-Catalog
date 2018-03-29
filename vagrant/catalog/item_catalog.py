import collections, random, string, json, requests, httplib2

from flask import Flask, url_for, render_template, request, redirect, make_response, flash, session
from sqlalchemy import create_engine, desc, distinct, inspect
from sqlalchemy.orm import sessionmaker
from oauth2client.client import flow_from_clientsecrets, FlowExchangeError

from database_setup import Base, Item, Riser, Limb, Arrow, Plunger, Sight, User

app = Flask(__name__)
engine = create_engine('sqlite:///archery_catalog.db')
Base.metadata.bind = engine
DBSession = sessionmaker(bind=engine)
db = DBSession()
CLIENT_ID = json.loads(open("client_secrets.json", "r").read())["web"]["client_id"]


@app.route("/")
def homePage():
    recent_items = db.query(Item).order_by(desc(Item.time_created)).limit(10)
    categories = [cls.__name__ for cls in Item.__subclasses__()]
    return render_template("index.html", items=recent_items, categories=categories)


@app.route("/category/<item_type>/")
def categoryPage(item_type):
    items = db.query(Item).filter(Item.type == item_type).order_by(desc(Item.time_created))
    if "username" not in session:
        return render_template("public_category_page.html", items=items, category=item_type)
    return render_template("category_page.html", items=items, category=item_type)


@app.route("/category/<item_type>/<int:item_id>/")
def itemPage(item_type, item_id):
    item = db.query(Item).filter(Item.id == item_id).first()
    fields = getDisplayDict(item)
    if "username" not in session or item.user_id != session["user_id"]:
        return render_template("public_item_page.html", item=item, fields=fields)
    return render_template("item_page.html", item=item, fields=fields)


@app.route("/category/<item_type>/new", methods=["GET", "POST"])
def newItemPage(item_type):
    if "username" not in session:
        return redirect(url_for("showLogin"))
    constructor = globals()[item_type]
    new_item = constructor()
    if request.method == "POST":
        for key, value in request.form.items():
            field_name = formatFieldName(key, undo=True)
            setattr(new_item, field_name, value)
        new_item.user_id = getUserID(session["email"])
        db.add(new_item)
        db.commit()
        flash("Successfully added %s." % new_item.name, "status")
        return redirect(url_for("categoryPage", item_type=item_type))
    else:
        fields = getDisplayDict(new_item)
        return render_template("new_item.html", fields=fields, item=new_item)


@app.route("/category/<item_type>/<int:item_id>/edit/", methods=["GET", "POST"])
def editItem(item_type, item_id):
    if "username" not in session:
        return redirect(url_for("showLogin"))
    item = db.query(Item).filter(Item.id == item_id).first()
    if not item:
        return redirect(url_for("categoryPage", item_type=item.type))
    if session["user_id"] != item.user_id:
        # user is attempting to visit the edit url of an item that isn't theirs
        flash("Cannot edit another user's item", "status")
        return redirect(url_for("itemPage", item_type=item_type, item_id=item_id))
    if request.method == "POST":
        for key, value in request.form.items():
            if value:
                field_name = formatFieldName(key, undo=True)
                setattr(item, field_name, value)
        db.add(item)
        db.commit()
        flash("Successfully updated %s." % item.name, "status")
        return redirect(url_for("itemPage", item_type=item_type, item_id=item.id))
    else:
        fields = getDisplayDict(item)
        return render_template("edit_item.html", fields=fields, item=item)


@app.route("/category/<item_type>/<int:item_id>/delete", methods=["GET", "POST"])
def deleteItemPage(item_type, item_id):
    if "username" not in session:
        return redirect(url_for("showLogin"))
    item = db.query(Item).filter(Item.id == item_id).first()
    if not item:
        # This handles the case where a user goes back and clicks cancel after already deleting an item
        return redirect(url_for("categoryPage", item_type=item_type))
    if session["user_id"] != item.user_id:
        # user is attempting to visit the delete url of an item that isn't theirs
        flash("Cannot delete another user's item.", "status")
        return redirect(url_for("itemPage", item_type=item_type, item_id=item_id))
    if request.method == "POST":
        db.delete(item)
        db.commit()
        flash("Successfully deleted %s." % item.name, "status")
        return redirect(url_for("categoryPage", item_type=item_type))
    else:
        return render_template("delete_item.html", item_type=item_type, item=item)


def getDisplayDict(item):
    """Returns a dictionary containing the user-facing fields of an item.
    Field names are formatted so that they contain no underscores and have
    the first letter of each word capitalized."""
    private_fields = ["id", "catalog_id", "time_created", "type", "catalog", "user", "user_id"]
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


# CODE ADAPTED FROM UDACITY -------------------------------------------
# https://github.com/udacity/ud330/blob/master/Lesson2/step6/project.py


@app.route("/login")
def showLogin():
    # Create anti-forgery state token
    state = ''.join(random.choice(string.ascii_uppercase + string.digits)
                    for x in xrange(32))
    session['state'] = state
    return render_template("login.html", STATE=state, client_id=CLIENT_ID, return_url=request.referrer)


@app.route('/gconnect', methods=['POST'])
def gconnect():
    # Validate state token
    if request.args.get('state') != session['state']:
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

    stored_access_token = session.get('access_token')
    stored_gplus_id = session.get('gplus_id')
    if stored_access_token is not None and gplus_id == stored_gplus_id:
        response = make_response(json.dumps('Current user is already connected.'),
                                 200)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Store the access token in the session for later use.
    session['access_token'] = credentials.access_token
    session['gplus_id'] = gplus_id

    # Get user info
    userinfo_url = "https://www.googleapis.com/oauth2/v1/userinfo"
    params = {'access_token': credentials.access_token, 'alt': 'json'}
    answer = requests.get(userinfo_url, params=params)

    data = answer.json()

    session['username'] = data['name']
    session['picture'] = data['picture']
    session['email'] = data['email']
    
    # Add user to database if they are not already present
    user_id = getUserID(session['email'])
    if not user_id:
        user_id = createUser(session)
    session['user_id'] = user_id

    output = ''
    output += '<h1>Welcome, '
    output += session['username']
    output += '!</h1>'
    output += '<img src="'
    output += session['picture']
    output += ' " style = "width: 300px; height: 300px;border-radius: 150px;-webkit-border-radius: 150px;-moz-border-radius: 150px;"> '
    print "done!"
    return output


@app.route('/gdisconnect')
def gdisconnect():
    access_token = session.get('access_token')
    if access_token is None:
        flash("No user is logged in.", "status")
        return redirect(request.referrer)
    print 'In gdisconnect access token is %s', access_token
    print 'User name is: '
    print session['username']
    url = 'https://accounts.google.com/o/oauth2/revoke?token=%s' % session['access_token']
    h = httplib2.Http()
    result = h.request(url, 'GET')[0]
    print 'result is '
    print result
    if result['status'] == '200':
        del session['access_token']
        del session['gplus_id']
        del session['username']
        del session['email']
        del session['picture']
        flash("Successfully signed out.", "status")
        return redirect(request.referrer)
    else:
        flash("Failed to revoke token for current user.", "status")
        return redirect(request.referrer)


def createUser(session):
    newUser = User(name=session['username'], email=session[
                   'email'], picture=session['picture'])
    db.add(newUser)
    db.commit()
    user = db.query(User).filter_by(email=session['email']).one()
    return user.id


def getUserInfo(user_id):
    user = db.query(User).filter_by(id=user_id).one()
    return user


def getUserID(email):
    try:
        user = db.query(User).filter_by(email=email).one()
        return user.id
    except:
        return None


# CODE ADAPTED FROM UDACITY -------------------------------------------
# https://github.com/udacity/ud330/blob/master/Lesson2/step6/project.py


if __name__ == '__main__':
    app.secret_key = "Robin_Hood_was_here"
    app.debug = True
    app.run(host = '0.0.0.0', port = 8000)