from flask import Flask, request, g, render_template, redirect, url_for
import os
import json
from flask_sqlalchemy import SQLAlchemy
from flask_login import (
    LoginManager, UserMixin, current_user,
    login_required, login_user, logout_user
)
from flask import Response
from flask import jsonify
from classes.Topology import Topology

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///tutorial.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.secret_key = 'super secret key'
app.config['SESSION_TYPE'] = 'filesystem'

db = SQLAlchemy(app)

topology = None

import logging

log = logging.getLogger('werkzeug')
log.setLevel(logging.ERROR)

static_folder_root = os.path.dirname(os.path.abspath(__file__))
ASSETS_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'static')

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(40), unique=True)
    password = db.Column(db.String(40))
    authenticated = db.Column(db.Boolean, default=False)

    def __init__(self, username, password):
        self.username = username
        self.password = password

    def is_active(self):
        """True, as all users are active."""
        return True

    def get_id(self):
        """Return the email address to satisfy Flask-Login's requirements."""
        return self.id

    def is_authenticated(self):
        """Return True if the user is authenticated."""
        return self.authenticated

    def is_anonymous(self):
        """False, as anonymous users aren't supported."""
        return False

    def __repr__(self):
        return '<User %r>' % self.username

login_manager = LoginManager()
login_manager.login_view = "login"

@login_manager.user_loader
def user_loader(user_id):
    """Given *user_id*, return the associated User object.

    :param unicode user_id: user_id (email) user to retrieve
    """
    return User.query.get(user_id)


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        name = request.form['username']
        user = User.query.filter_by(username=name).first()
        if user:
            if user.password == request.form['password']:
                # Login and validate the user.
                # user should be an instance of your `User` class
                user.authenticated = True
                db.session.add(user)
                db.session.commit()
                login_user(user)

                return redirect(url_for('index'))
    return render_template('login.html')

@app.route('/logout', methods=['GET'])
@login_required
def logout():
    user = current_user
    user.authenticated = False
    for node in app.config[str(current_user.id)].nameToNode.values():
        if node.nodeType == "Switches":
            node.stop()
        else:
            node.terminate()
    db.session.add(user)
    db.session.commit()
    logout_user()
    return redirect(url_for('login'))

@app.route('/static/<path:filename>')
def serveStatic(filename):
    root_dir = os.path.dirname(os.getcwd())
    return send_from_directory(os.path.join(root_dir, 'static', 'js'),   filename)

@app.route("/")
@login_required
def index():
    userid = current_user.id
    topology = Topology(user_id=userid)
    app.config[str(current_user.id)] = topology
    app.config[str(current_user.id)].start()
    print(str(app.config[str(current_user.id)]))
    return app.send_static_file('index.html')

@app.route("/getSavedTopo")
@login_required
def getSavedTopo():
    try:
        f = open(app.config[str(current_user.id)].configFile, 'r')
        data = json.load(f)
    except:
        data = {}
    return jsonify(data)

@app.route("/getParams")
@login_required
def getParams():
    return app.config[str(current_user.id)].getParams(request.args.get('id'))

@app.route("/postParams", methods=['POST'])
@login_required
def postParams():
    return app.config[str(current_user.id)].setParams(request.form['id'], json.loads(request.form['config']))

@app.route("/postAddNode", methods=['POST'])
@login_required
def postAddNode():
    return app.config[str(current_user.id)].addNode(request.form['type'], request.form['x'], request.form['y'])

@app.route("/postDelNode", methods=['POST'])
@login_required
def postDelNode():
    return app.config[str(current_user.id)].delNode(request.form['id'])

@app.route("/postAddLink", methods=['POST'])
@login_required
def postAddLink():
    return app.config[str(current_user.id)].setLink(request.form['firstId'], request.form['secondId'])

@app.route("/postDelLink", methods=['POST'])
@login_required
def postDelLink():
    return app.config[str(current_user.id)].delLink(request.form['firstId'], request.form['secondId'])

@app.route("/getPing", methods=['GET'])
@login_required
def getPing():
    try:
        return app.config[str(current_user.id)].ping(request.args.get('sender'), request.args.get('receiver'))
    except:
        return 'Internal error'

@app.route("/shutdown", methods=['POST']) 
@login_required
def shutdown():
    func = request.environ.get('werkzeug.server.shutdown')
    if func is None:
        raise RuntimeError('Not running with the Werkzeug Server')
    if request.form['param'] == 'clear':
        for node in app.config[str(current_user.id)].nameToNode.keys():
            if node.startswith('S') or node.startswith('H') or node.startswith('R'):
                app.config[str(current_user.id)].delNode(node)
    else:
        app.config[str(current_user.id)].stop()
    func()
    return Response('Server shutting down...', mimetype='text/plain')

db.init_app(app)
login_manager.init_app(app)

if __name__ == "__main__":
    app.run(host='0.0.0.0', threaded=True)

