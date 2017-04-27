from flask import Flask, request
import os
import json
from flask import Response
from flask import jsonify

app = Flask(__name__)

import logging

log = logging.getLogger('werkzeug')
log.setLevel(logging.ERROR)

static_folder_root = os.path.dirname(os.path.abspath(__file__))

@app.route("/")
def index():
    return app.send_static_file('index.html')

@app.route("/getSavedTopo")
def getSavedTopo():
    try:
        f = open('config.json', 'r')
        data = json.load(f)
    except:
        data = {}
    return jsonify(data)

@app.route("/getParams")
def getParams():
    id = request.args.get('id')
    #return topology.getParams(id)
    return 'S1'

@app.route("/postParams", methods=['POST'])
def postParams():
    id = request.form['id']
    config = request.form['config']
    #return topology.setParams(id, config)
    return 'success'

@app.route("/postAddNode", methods=['POST'])
def postAddNode():
    type = request.form['type']
    #return topology.addNode(type)
    return 'H1'

@app.route("/postDelNode", methods=['POST'])
def postDelNode():
    id = request.form['id']
    #topology.delNode(id)
    return 'success'

@app.route("/postSaveTopo", methods=['POST'])
def postSaveTopo():
    config = request.form['config']
    try:
        f = open('config.json', 'w')
        f.write(config)
        f.close()
    except:
        f.close()
    return 'success'

@app.route("/postAddLink", methods=['POST'])
def postAddLink():
    first = request.form['firstId']
    second = request.form['secondId']
    #return topology.addLink(first, second)
    return 'success'

@app.route("/postDelLink", methods=['POST'])
def postDelLink():
    first = request.form['firstId']
    second = request.form['secondId']
    #return topology.delLink(first, second)
    return 'success'

@app.route("/getPing", methods=['GET'])
def getPing():
    sender = request.args.get('sender')
    receiver = request.args.get('receiver')
    #return topology.ping(sender, receiver)
    return "ping success"

@app.route("/shutdown", methods=['POST']) 
def shutdown():
    func = request.environ.get('werkzeug.server.shutdown')
    if func is None:
        raise RuntimeError('Not running with the Werkzeug Server')
    func()
    return Response('Server shutting down...', mimetype='text/plain')

if __name__ == "__main__":
    #topology = Topology()
    app.run(host='0.0.0.0')

