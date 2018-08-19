from flask import Blueprint, request, session
from flask import render_template, redirect, jsonify
from flask import Response

from werkzeug.security import gen_salt
from authlib.flask.oauth2 import current_token
from authlib.specs.rfc6749 import OAuth2Error
from .models import db, User, OAuth2Client
from .oauth2 import authorization, require_oauth
from pprint import pprint


bp = Blueprint(__name__, 'home')


def current_user():
    if 'id' in session:
        uid = session['id']
        return User.query.get(uid)
    return None

@bp.route('/')
def home():
    user = current_user()
    if user:
        clients = OAuth2Client.query.filter_by(user_id=user.id).all()
    else:
        clients = []
    return render_template('home.html', user=user, clients=clients)


@bp.route('/login', methods=('GET', 'POST'))
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        email = request.form.get('email')
        user = User.query.filter_by(username=username, userpass=password).first()

        if not user:
            user = User(username=username, userpass=password)
            db.session.add(user)
            db.session.commit()
        session['id'] = user.id
        return redirect('/')
    return redirect('/')


@bp.route('/fail_login')
def fail_login():
    return render_template('fail_login.html')


@bp.route('/logout')
def logout():
    del session['id']
    return redirect('/')


@bp.route('/create_client', methods=('GET', 'POST'))
def create_client():
    user = current_user()
    if not user:
        return redirect('/')
    if request.method == 'GET':
        return render_template('create_client.html')
    client = OAuth2Client(**request.form.to_dict(flat=True))
    client.user_id = user.id
    client.client_id = gen_salt(24)
    if client.token_endpoint_auth_method == 'none':
        client.client_secret = ''
    else:
        client.client_secret = gen_salt(48)
    db.session.add(client)
    db.session.commit()
    return redirect('/')


@bp.route('/oauth/authorize', methods=['GET', 'POST'])
def authorize():
    user = current_user()
    if request.method == 'GET':
        try:
            grant = authorization.validate_consent_request(end_user=user)
        except OAuth2Error as error:
            return error.error
        return render_template('authorize.html', user=user, grant=grant)
    if not user and 'username' in request.form:
        username = request.form.get('username')
        user = User.query.filter_by(username=username).first()
    if request.form['confirm']:
        grant_user = user
    else:
        grant_user = None
    return authorization.create_authorization_response(grant_user=grant_user)

@bp.route('/sunho', methods=['POST'])
def sunho():
    if request.method == 'POST':

        r = Response(response=render_template('iot_clova.json'), status=200, mimetype="application/json")
        r.headers["Content-Type"] = "application/json; charset=utf-8"
        pprint(request.form) 
        return r
        # return render_template('iot_clova.json')
    return render_template('sunho.html')

@bp.route('/oauth/token', methods=['POST'])
def issue_token():
    return authorization.create_token_response()


@bp.route('/oauth/revoke', methods=['POST'])
def revoke_token():
    return authorization.create_endpoint_response('revocation')


@bp.route('/api/me')
@require_oauth('device')
def api_me():
    user = current_token.user
    return jsonify(id=user.id, username=user.username)

