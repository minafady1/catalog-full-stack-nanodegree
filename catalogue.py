from flask import Flask, render_template
from flask import request, redirect, jsonify, url_for, flash
from sqlalchemy import create_engine, asc
from sqlalchemy.orm import sessionmaker
from database_setup import Category, Base, Item, User
from flask import session as login_session
import random
import string
from oauth2client.client import flow_from_clientsecrets
from oauth2client.client import FlowExchangeError
import httplib2
import json
from flask import make_response
import requests
from functools import wraps

app = Flask(__name__)

CLIENT_ID = json.loads(
        open('client_secrets.json', 'r').read())['web']['client_id']

engine = create_engine('postgresql://catalog:123@localhost/catalog')
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
session = DBSession()


def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'username' in login_session:
            return f(*args, **kwargs)
        else:
            return redirect(url_for('showLogin', next=request.url))
    return decorated_function


# Create a state token to prevent request forgery and store it in the session.
@app.route('/login')
def showLogin():
    state = ''.join(random.choice(string.ascii_uppercase + string.digits)
                    for x in xrange(32))
    login_session['state'] = state
    return render_template('login.html', STATE=state)

# Connect user using Google Plus account.
@app.route('/gconnect', methods=['POST'])
def gconnect():
    # Validate state token
    if request.args.get('state') != login_session['state']:
        response = make_response(json.dumps('Invalid state parameter'), 401)
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
        response = make_response(json.dumps('''Failed to upgrade
                                            the authorization code.'''), 401)
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
        response = make_response(json.dumps("""Token's user ID doesn't
                                            match given user ID"""), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    #Verify that the access token is valid for this app
    if result['issued_to'] != CLIENT_ID:
        response = make_response(json.dumps("""Token's client ID doesn't 
                                            match app's"""), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
   #Check to see if user is already logged in
    stored_access_token = login_session.get('access_token')
    stored_gplus_id = login_session.get('gplus_id')
    if stored_access_token is not None and gplus_id == stored_gplus_id:
        response = make_response(json.dumps('''Current user is already
                                            connected'''), 200)
        response.headers['Content-Type'] = 'application/json'
        return response

   #Store the access token in the session for later use
    login_session['access_token'] = credentials.access_token
    login_session['gplus_id'] = gplus_id

    #Get user info and store in login session for later use
    userinfo_url = "https://www.googleapis.com/oauth2/v1/userinfo"
    params = {'access_token': credentials.access_token, 'alt':'json'}
    answer = requests.get(userinfo_url, params=params)
    data = json.loads(answer.text)

    login_session['username'] = data['name']
    login_session['picture'] = data['picture']
    login_session['email'] = data['email']

    #See if user exists, if it doesn't make a new one
    user_id = getUserID(login_session['email'])
    if not user_id:
        user_id = createUser(login_session)
    login_session['user_id'] = user_id

    #Render welcome message if user logged in successfully
    output = ''
    output += '<h1>Welcome, '
    output += login_session['username']
    output += '!</h1>'
    output += '<img src="'
    output += login_session['picture']
    output += ''' " style = "width: 300px; height: 300px;border-radius: 150px;
                -webkit-border-radius: 150px;-moz-border-radius: 150px;"> '''
    print ("done!")
    return output
@app.route('/gdisconnect')
def gdisconnect():
    access_token = login_session['access_token']

    """Ensure to only disconnect a connected user"""
    if access_token is None:
        response = make_response(json.dumps('Current user not connected'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    """Execute HTTP GET request to revoke current token"""
    url = 'https://accounts.google.com/o/oauth2/revoke?token=%s' % login_session['access_token']
    h = httplib2.Http()
    result = h.request(url, 'GET')[0]

    if result['status'] == '200':
        """Reset the user's session"""
        del login_session['access_token']
        del login_session['gplus_id']
        del login_session['username']
        del login_session['email']
        del login_session['picture']

        return redirect(url_for('showCategory'))
    else:
        """If the given token was invalid, do the following"""
        response = make_response(json.dumps("""Failed to revoke token 
                                            for given user"""), 400)
        response.headers['Content-Type'] = 'application/json'
        return response


@app.route('/fbconnect', methods=['POST'])
def fbconnect():
    if request.args.get('state') != login_session['state']:
        response = make_response(json.dumps('Invalid state parameter.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    access_token = request.data

    """Exchange short-lived token for long-lived token"""
    app_id = json.loads(open('fbclient_secrets.json', 'r').read())[
        'web']['app_id']
    app_secret = json.loads(
        open('fbclient_secrets.json', 'r').read())['web']['app_secret']
    url = 'https://graph.facebook.com/oauth/access_token?grant_type=fb_exchange_token&client_id=%s&client_secret=%s&fb_exchange_token=%s' % (app_id, app_secret, access_token)
    h = httplib2.Http()
    result = h.request(url, 'GET')[1]

    """Use token to get user info from API"""
    userinfo_url = "https://graph.facebook.com/v2.4/me"
    # strip expire tag from access token.
    token = result.split("&")[0]

    url = 'https://graph.facebook.com/v2.4/me?%s&fields=name,id,email' % token
    h = httplib2.Http()
    result = h.request(url, 'GET')[1]

    """Store user info for later use"""
    data = json.loads(result)
    login_session['provider'] = 'facebook'
    login_session['username'] = data["name"]
    login_session['email'] = data["email"]
    login_session['facebook_id'] = data["id"]

    """The token must be stored in the login_session in
    order to properly logout, let's strip out the information before the
    equals sign in our token"""
    stored_token = token.split("=")[1]
    login_session['access_token'] = stored_token

    """Get user picture"""
    url = 'https://graph.facebook.com/v2.4/me/picture?%s&redirect=0&height=200&width=200' % token
    h = httplib2.Http()
    result = h.request(url, 'GET')[1]
    data = json.loads(result)

    login_session['picture'] = data["data"]["url"]

    """Check if user exists, if not then create user"""
    user_id = getUserID(login_session['email'])
    if not user_id:
        user_id = createUser(login_session)
    login_session['user_id'] = user_id

    """If user logged in successfully, render welcome message"""
    output = ''
    output += '<h1>Welcome, '
    output += login_session['username']
    output += '!</h1>'
    output += '<img src="'
    output += login_session['picture']
    output += ''' " style = "width: 300px; height: 300px;border-radius: 150px;
            -webkit-border-radius: 150px;-moz-border-radius: 150px;">'''

    flash("You Are Now Logged In As %s" % login_session['username'])
    return output

# Disconnect Facebook user
@app.route('/fbdisconnect')
def fbdisconnect():
    facebook_id = login_session['facebook_id']
    access_token = login_session['access_token']

    """Ensure to only disconnect a connected user"""
    if access_token is None:
        response = make_response(json.dumps('Current user not connected'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    url = 'https://graph.facebook.com/%s/permissions?access_token=%s' % (
            facebook_id,access_token)
    h = httplib2.Http()
    result = h.request(url, 'DELETE')[1]

    """Reset the user's session"""
    del login_session['provider']
    del login_session['username']
    del login_session['email']
    del login_session['facebook_id']

    flash("You've successfully logged out")
    return redirect(url_for('showCategory'))  

@app.route('/disconnect')
def disconnect():
    try:
        if login_session['provider'] == 'facebook':
            return redirect('/fbdisconnect')
    except:
        return redirect('/gdisconnect')
  
@app.route('/')
@app.route('/category/')
def showCategory():
    category = session.query(Category).order_by(asc(Category.name))
    if 'id' not in login_session:
         return render_template('category1.htm',categories=category)
    else:
        return render_template('category.html', categories=category)



@app.route('/category/<string:category_name>/')
@app.route('/category/<string:category_name>/items/')
def showMenu(category_name):
    category = session.query(Category).filter_by(name=category_name).one()
    items = session.query(Item).filter_by(
        category_name=category_name).all()
    if 'id' not in login_session:
         return render_template('item1.html', items=items, category=category)
    else:
        return render_template('item.html', items=items, category=category)




@app.route('/category/<string:category_name>/<string:item_name>')
@app.route('/category/<string:category_name>/<string:item_name>/')
def showDes(item_name,category_name):
    
    items = session.query(Item).filter_by(
        name=item_name).all()
    return render_template('description.html', items=items)


@app.route('/category/<string:category_name>/<string:item_name>/delete', methods=['GET', 'POST'])
def deleteItem(item_name,category_name):
    if request.method == 'POST':
        itemToDelete = session.query(Item).filter_by(name=item_name).one()
        if itemToDelete.user_id != login_session['user_id']:
            return """<script>function myFunction() {alert('You are not
                authorized to delete this item. Please create your own item """ \
               "in order to delete.');}</script><body onload='myFunction()'>"
        session.delete(itemToDelete)
        session.commit()
        return redirect(url_for('showMenu', category_name=category_name))
    else:
        return render_template('deletitem.html', category_name=category_name,item_name=item_name)


@app.route('/category/<string:category_name>/new', methods=['GET', 'POST'])
def newItem(category_name):
    if request.method == 'POST':
        newItem=Item(name=request.form['name'],description=request.form['des'],
                     category_name=category_name,user_id=login_session['user_id'])
        session.add(newItem)
        session.commit()
        flash("new menu item created")
        return redirect(url_for('showMenu',category_name=category_name))
    else:
        return render_template('newItem.html',category_name=category_name)

@app.route('/category/<string:category_name>/<string:item_name>/edite', methods=['GET', 'POST'])
def editItem(item_name,category_name):
    if request.method == 'POST':
        item=session.query(Item).filter_by(name=item_name).one()
        if item.user_id != login_session['user_id']:
            return """<script>function myFunction() {alert('You are not
                    authorized to edit this item. Please create your own item """ \
               "in order to edit.');}</script><body onload='myFunction()'>"
        item.name=request.form['name']
        item.description=request.form['des'],
        session.add(item)
        session.commit()
        return redirect(url_for('showMenu',category_name=category_name))
    else:
        return render_template('editeItem.html',category_name=category_name,item_name=item_name)
    
    
@app.route('/category/new/', methods=['GET', 'POST'])
def newCategory():
    if request.method == 'POST':
        new = Category(
            name=request.form['name'], user_id=1)
        session.add(new)
        session.commit()
        return redirect(url_for('showCategory'))
    else:
        return render_template('newcatagory.html')
        
@app.route('/catalog.JSON')
def catalogJSON():
    categories = session.query(Category).all()
    items = session.query(Item).all()
    return jsonify(Categories = [c.serialize for c in categories],
                   Items = [i.serialize for i in items])
@app.route('/categories.json')
def categoriesJSON():
    categories = session.query(Category).all()
    return jsonify(Categories = [c.serialize for c in categories])

# API endpoints for all items of a specific category.
@app.route('/<category_name>/items.json')
def itemsJSON(category_name):
    category = session.query(Category).filter_by(name=category_name).one()
    items = session.query(Item).filter_by(category=category).all()
    return jsonify(Items = [i.serialize for i in items])

@app.route('/category/<string:category_name>/<string:item_name>/JSON')
def menuItemJSON(category_name, item_name):
    Items = session.query(Item).filter_by(name=item_name).one()
    return jsonify(Item=Items.serialize)

#get user id
def getUserID(email):
    try:
        user = session.query(User).filter_by(email=email).one()
        return user.id
    except:
        return None

# Get user info
def getUserInfo(user_id):
    user = session.query(User).filter_by(id=user_id).one()
    return user

# Create a new user
def createUser(login_session):
    newUser = User(name=login_session['username'], email=login_session['email'],
                   picture=login_session['picture'])
    session.add(newUser)
    session.commit()
    user = session.query(User).filter_by(email=login_session['email']).one()
    return user.id

if __name__ == '__main__':
    app.secret_key = 'super_secret_key'
    app.debug = True
    app.run(host='0.0.0.0', port=8000)
