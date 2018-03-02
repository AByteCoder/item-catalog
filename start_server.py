#!/usr/bin/python3

from flask import Flask, url_for, render_template, session, make_response
from flask import jsonify, request, redirect
from flaskext.markdown import Markdown
from datetime import datetime
from sqlalchemy import desc
import json
import random
import string
from database import db_session, User, Category, CategoryItem
from oauth2client.client import flow_from_clientsecrets
from oauth2client.client import FlowExchangeError
import httplib2
import requests


# contains all the flask related code

app = Flask(__name__)
Markdown(app)
app_id = '1014045698744557'
client_json = None

# read google client secret for later use
with open('client_secret.json') as file:
    client_json = json.loads(file.read())


# home page route
@app.route('/', methods=['GET'])
@app.route('/index', methods=['GET'])
def home():
    state = ''.join(random.choice(string.ascii_uppercase + string.digits)
                    for x in range(32))
    session['state'] = state
    if session.get('id', 0) != 0:
        login = session
    else:
        login = False
    categories = db_session.query(Category).all()
    items = db_session.query(CategoryItem).\
        order_by(desc(CategoryItem.latest_update)).limit(10).all()
    return render_template('index.html',
                           state=state, client=client_json['web']['client_id'],
                           appid=app_id, login=login, categories=categories,
                           items=items, title="Item Catalog::Home")


# google api disconnect
@app.route('/api/v1/gdisconnect')
def gdisconnect():
    access_token = session.get('access_token')
    if access_token is None:
        response = make_response(json.dumps('Current user not connected.'),
                                 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    url = 'https://accounts.google.com/o/oauth2/revoke?token=%s'\
        % session['access_token']
    h = httplib2.Http()
    result = h.request(url, 'GET')[0]
    if result['status'] == '200':
        del session['access_token']
        del session['gplus_id']
        del session['username']
        del session['email']
        del session['pic']
        response = make_response(json.dumps('Successfully disconnected.'), 200)
        response.headers['Content-Type'] = 'application/json'
        return response
    else:
        response = make_response(
            json.dumps('Failed to revoke token for given user.', 400))
        response.headers['Content-Type'] = 'application/json'
    return response


# facebook api connected
@app.route('/api/v1/fconnect', methods=['POST'])
def fb():
    if request.args.get('state') != session['state']:
        response = make_response(json.dumps('Invalid state parameter.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    auth = request.json
    session['username'] = auth['name']
    session['pic'] = auth['picture']
    session['email'] = auth['email']
    session['provider'] = 'fb'

    user_list = db_session.query(User).\
        filter(User.email == session['email']).all()
    # create user if not present
    if len(user_list) == 0:
        us = User(name=auth['name'], email=auth['email'], pic=auth['picture'])
        db_session.add(us)
        db_session.commit()
        user = db_session.query(User).\
            filter(User.email == session['email']).one()
        session['id'] = user.id
    else:
        session['id'] = user_list[0].id
    res = make_response(json.dumps({
        'name': auth['name'], 'pic': auth['picture'],
        'email': auth['email']}), 200)
    res.headers['Content-Type'] = 'application/json'
    return res


# route for adding category
@app.route('/api/v1/addCategory', methods=['POST'])
def addCategory():
    if session.get('id', 0) != 0:
        id = session['id']
        name = request.json['name']
        desc = request.json['description']
        c = Category(name=name, description=desc, created_by=id)
        db_session.add(c)
        db_session.commit()
        res = make_response(json.dumps({'id': c.id, 'msg': "category added"}),
                            200)
        res.headers['Content-Type'] = 'application/json'
        return res
    else:
        res = make_response(json.dumps("forbidden"), 403)
        res.headers['Content-Type'] = 'application/json'
        return res


# route for adding item
@app.route('/api/v1/addItem', methods=['POST'])
def apiAddCategory():
    if session.get('id', 0) != 0:
        id = session['id']
        name = request.json['name']
        desc = request.json['description']
        cid = request.json['cid']
        c = CategoryItem(name=name, description=desc, created_by=id,
                         belongs_to=cid)
        db_session.add(c)
        db_session.commit()
        res = make_response(json.dumps({'id': c.id, 'msg': "item added"}), 200)
        res.headers['Content-Type'] = 'application/json'
        return res
    else:
        res = make_response(json.dumps("forbidden"), 403)
        res.headers['Content-Type'] = 'application/json'
        return res


# categories page
@app.route('/categories/<int:id>')
def catHtml(id):
    try:
        if session.get('id', 0) != 0:
            login = session
        else:
            login = False
        c = db_session.query(Category).filter(Category.id == id).one()
        categories = db_session.query(Category).all()
        return render_template('category.html',
                               state=session['state'],
                               client=client_json['web']['client_id'],
                               appid=app_id, login=login,
                               categories=categories,
                               category=c, title=c.name)
    except Exception as e:
        print(e)
        res = make_response('<h3>Invalid Category</h3>')
        return res


# user profile page
@app.route('/users/<int:id>/', methods=['GET'])
def userProfile(id):
    try:
        if session.get('id', 0) != 0:
            login = session
        else:
            login = False
        u = db_session.query(User).filter(User.id == id).one()
        categories = db_session.query(Category).all()
        return render_template('profile.html',
                               state=session['state'],
                               client=client_json['web']['client_id'],
                               appid=app_id,
                               login=login,
                               categories=categories,
                               user=u,
                               title=u.name+"'s Profile")
    except Exception as e:
        print(e)
        res = make_response("<h1>user not found </h1>", 404)
        return res


# items page
@app.route('/items/<int:id>')
def itemHtml(id):
    try:
        if session.get('id', 0) != 0:
            login = session
        else:
            login = False
        c = db_session.query(CategoryItem).filter(CategoryItem.id == id).one()
        categories = db_session.query(Category).all()
        return render_template('item.html',
                               state=session['state'],
                               client=client_json['web']['client_id'],
                               appid=app_id,
                               login=login,
                               categories=categories,
                               item=c, title=c.name)
    except Exception as e:
        print(e)
        res = make_response('<h3>Invalid Item</h3>')
        return res


# sign in using google account
@app.route('/api/v1/gconnect', methods=['POST'])
def google():
    # Validate state token
    if request.args.get('state') != session['state']:
        response = make_response(json.dumps('Invalid state parameter.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    # Obtain authorization code
    code = request.data

    try:
        # Upgrade the authorization code into a credentials object
        oauth_flow = flow_from_clientsecrets('client_secret.json',
                                             scope='profile')
        oauth_flow.redirect_uri = 'postmessage'
        credentials = oauth_flow.step2_exchange(code)
    except FlowExchangeError:
        response = make_response(json.dumps('Failed to upgrade the \
                                            authorization code.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Check that the access token is valid.
    access_token = credentials.access_token
    url = ('https://www.googleapis.com/oauth2/v1/tokeninfo?access_token=%s'
           % access_token)
    h = httplib2.Http()
    result = json.loads(h.request(url, 'GET')[1].decode('utf8'))
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
    if result['issued_to'] != client_json["web"]["client_id"]:
        response = make_response(
            json.dumps("Token's client ID does not match app's."), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    stored_access_token = session.get('access_token')
    stored_gplus_id = session.get('gplus_id')
    if stored_access_token is not None and gplus_id == stored_gplus_id:
        res = make_response(json.dumps({'name': session['username'],
                                        'email': session['email'],
                                        'pic': session['pic'],
                                        'alreadyLogged': True}), 200)
        res.headers['Content-Type'] = 'application/json'
        return res

    # Store the access token in the session for later use.
    session['access_token'] = credentials.access_token
    session['gplus_id'] = gplus_id

    # Get user info
    userinfo_url = "https://www.googleapis.com/oauth2/v1/userinfo"
    params = {'access_token': credentials.access_token, 'alt': 'json'}
    answer = requests.get(userinfo_url, params=params)
    data = answer.json()

    if data['name'] == '':
        name = data['email'].split('@')[0]
    else:
        name = data['name']

    session['username'] = name
    session['pic'] = data['picture']
    session['email'] = data['email']
    session['provider'] = 'google'

    user_l = db_session.query(User).filter(User.email == session['email'])
    user_list = user_l.all()
    # create user if not present
    if len(user_list) == 0:
        us = User(name=name, email=data['email'], pic=data['picture'])
        db_session.add(us)
        db_session.commit()
        user_d = db_session.query(User).filter(User.email == session['email'])
        user = user_d.one()
        session['id'] = user.id
    else:
        session['id'] = user_list[0].id

    res = make_response(json.dumps({'name': session['username'],
                                    'email': data['email'],
                                    'pic': data['picture'],
                                    'alreadyLogged': False}), 200)
    res.headers['Content-Type'] = 'application/json'
    return res


# json api for a summary of all categories
@app.route('/api/v1/catalog/', methods=['GET'])
def catalog():
    categories = db_session.query(Category).order_by(Category.id).all()
    return jsonify(categories=[cat.serialize for cat in categories])


# json api to get,delete and update individual category information
@app.route('/api/v1/categories/<int:id>/', methods=['GET', 'DELETE', 'PUT'])
def category(id):
    try:
        c = db_session.query(Category).filter(Category.id == id).one()
        if request.method == 'GET':
            return jsonify(c.serialize)
        elif request.method == 'DELETE':
            # check if used has logged in
            if session.get('id', 0) == 0:
                res = make_response(json.dumps("forbidden"), 403)
                res.headers['Content-Type'] = 'application/json'
                return res
            else:
                # check if the logged in user is the owner
                if session['id'] != c.created_by:
                    res = make_response(json.dumps("forbidden"), 403)
                    res.headers['Content-Type'] = 'application/json'
                    return res
                else:
                    # cleared criteria perform operation
                    db_session.delete(c)
                    db_session.commit()
                    res = make_response(json.dumps("deleted category\
                                                    successfully"), 200)
                    res.headers['Content-Type'] = 'application/json'
                    return res
        else:
            if session.get('id', 0) == 0:
                res = make_response(json.dumps("forbidden"), 403)
                res.headers['Content-Type'] = 'application/json'
                return res
            else:
                if session['id'] != c.created_by:
                    res = make_response(json.dumps("forbidden"), 403)
                    res.headers['Content-Type'] = 'application/json'
                    return res
                else:
                    if request.json is not None:
                        # check if request is in JSON format
                        j = request.json
                        c.name = j['name']
                        c.description = j['description']
                        c.latest_update = datetime.utcnow()
                        db_session.commit()
                        res = make_response(json.dumps("item updated \
                                                        successfully"), 200)
                        res.headers['Content-Type'] = 'application/json'
                        return res
                    else:
                        res = make_response(json.dumps("request should be \
                                                        a valid JSON"), 400)
                        res.headers['Content-Type'] = 'application/json'
                        return res
    except Exception as e:
        print(e)
        res = make_response(json.dumps("category not found"), 404)
        res.headers['Content-Type'] = 'application/json'
        return res


# get info about user in JSON format
@app.route('/api/v1/users/<int:id>/', methods=['GET'])
def user(id):
    try:
        u = db_session.query(User).filter(User.id == id).one()
        return jsonify(u.serialize)
    except Exception as e:
        print(e)
        res = make_response(json.dumps("user not found"), 404)
        res.headers['Content-Type'] = 'application/json'
        return res


# get/update/delete info about items in JSON format
@app.route('/api/v1/items/<int:id>/', methods=['GET', 'DELETE', 'PUT'])
def item(id):
    try:
        i = db_session.query(CategoryItem).filter(CategoryItem.id == id).one()
        if request.method == 'GET':
            return jsonify(i.serialize)
        elif request.method == 'DELETE':
            if session.get('id', 0) == 0:
                res = make_response(json.dumps("forbidden"), 403)
                res.headers['Content-Type'] = 'application/json'
                return res
            else:
                if session['id'] != i.created_by:
                    res = make_response(json.dumps("forbidden"), 403)
                    res.headers['Content-Type'] = 'application/json'
                    return res
                else:
                    db_session.delete(i)
                    db_session.commit()
                    res = make_response(json.dumps("deleted item successfully"
                                                   ), 200)
                    res.headers['Content-Type'] = 'application/json'
                    return res
        else:
            if session.get('id', 0) == 0:
                res = make_response(json.dumps("forbidden"), 403)
                res.headers['Content-Type'] = 'application/json'
                return res
            else:
                if session['id'] != i.created_by:
                    res = make_response(json.dumps("forbidden"), 403)
                    res.headers['Content-Type'] = 'application/json'
                    return res
                else:
                    if request.json is not None:
                        j = request.json
                        i.name = j['name']
                        i.description = j['description']
                        i.latest_update = datetime.utcnow()
                        db_session.commit()
                        res = make_response(json.dumps("item updated \
                                                        successfully"), 200)
                        res.headers['Content-Type'] = 'application/json'
                        return res
                    else:
                        res = make_response(json.dumps("request should be a \
                                                        valid JSON"), 400)
                        res.headers['Content-Type'] = 'application/json'
                        return res

    except Exception as e:
        print(e)
        res = make_response(json.dumps("item not found"), 404)
        res.headers['Content-Type'] = 'application/json'
        return res


# logout from the application
@app.route('/logout')
def logout():
    if session.get('id', 0) != 0:
        del session['id']
        if session['provider'] == "google":
            gdisconnect()
            redirect("/")
    return redirect("/")


if __name__ == "__main__":
    app.secret_key = ' 73RKJLNKGRXGX2CLH7KONEASLITQGLBK '
    app.run(host='0.0.0.0', port=5000, debug=True)
