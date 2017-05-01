from flask import Flask, request, g
import os
import json
from flask import Response
from flask import jsonify
from classes.Topology import Topology

app = Flask(__name__)
topology = Topology(topo=None)

import logging

log = logging.getLogger('werkzeug')
log.setLevel(logging.ERROR)

static_folder_root = os.path.dirname(os.path.abspath(__file__))
ASSETS_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'static')

@app.route('/static/<path:filename>')
def serveStatic(filename):
    root_dir = os.path.dirname(os.getcwd())
    return send_from_directory(os.path.join(root_dir, 'static', 'js'),   filename)

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
    global topology
    return topology.getParams(id)

@app.route("/postParams", methods=['POST'])
def postParams():
    id = request.form['id']
    config = json.loads(request.form['config'])
    global topology
    return topology.setParams(id, config)

@app.route("/postAddNode", methods=['POST'])
def postAddNode():
    type = request.form['type']
    global topology
    return topology.addNode(type)

@app.route("/postDelNode", methods=['POST'])
def postDelNode():
    id = request.form['id']
    global topology
    return topology.delNode(id)

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
    global topology
    return topology.addLink(first, second)

@app.route("/postDelLink", methods=['POST'])
def postDelLink():
    first = request.form['firstId']
    second = request.form['secondId']
    global topology
    return topology.delLink(first, second)

@app.route("/getPing", methods=['GET'])
def getPing():
    sender = request.args.get('sender')
    receiver = request.args.get('receiver')
    global topology
    return topology.ping(sender, receiver)

@app.route("/shutdown", methods=['POST']) 
def shutdown():
    func = request.environ.get('werkzeug.server.shutdown')
    if func is None:
        raise RuntimeError('Not running with the Werkzeug Server')
    global topology
    if request.form['param'] == 'clear':
        for node in topology.nameToNode.keys():
            if node.startswith('S') or node.startswith('H'):
                topology.delNode(node)
    else:
        topology.stop()
    func()
    return Response('Server shutting down...', mimetype='text/plain')

if __name__ == "__main__":
    topology.start()
    app.run(host='0.0.0.0')

