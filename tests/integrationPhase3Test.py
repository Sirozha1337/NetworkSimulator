import unittest
import sys
import os.path
import os
import json
import time
sys.path.append(".")
from Builder import app
import requests
from threading import Thread

class integrationPhase3Test(unittest.TestCase):
    def setUp(self):
        # Remove any topology if there were any saved
        with open('config.json', 'w+') as f:
            f.write('{ }')
            f.close()
        os.spawnl(os.P_NOWAIT, '/usr/bin/python', 'python',  'Builder.py')
        time.sleep(1)

    def testPostAddNode(self):
        self.assertEqual(self.AddNode('Hosts'), 'H1')
        self.assertEqual(self.AddNode('Switches'), 'S1')
        self.assertEqual(self.AddNode('Hosts'), 'H2')
        self.assertEqual(self.AddNode('Switches'), 'S2')

    def testGetParams(self):
        # Add switch
        self.assertEqual(self.AddNode('Switches'), 'S1')
        # Get switch params
        payload = {'id': 'S1'}
        r = requests.get("http://localhost:5000/getParams", params=payload)
        self.assertEqual(json.loads(r.text), json.loads('{"State": false, "DPID": 1, "Name": "S1", "ID":"S1", "x": 10, "y":15}'))
        # Add host
        self.assertEqual(self.AddNode('Hosts'), 'H1')
        # Get host params
        payload = {'id': 'H1'}
        r = requests.get("http://localhost:5000/getParams", params=payload)
        self.assertEqual(json.loads(r.text), json.loads('{"Name": "H1", "ID":"H1", "x": 10, "y":15}'))

    def testSetParams(self):
        #add node
        self.assertEqual(self.AddNode('Hosts'), 'H1')
        #test change node params
        payload = {'id' : 'H1', 'config' : '{ "Name" : "Host1", "ID" : "H1", "x": 10, "y":15 }' }
        r = requests.post("http://localhost:5000/postParams", data=payload)
        self.assertEqual(r.text, 'success')
        # Check if the parameters changed correctly
        payload = {'id': 'H1'}
        r = requests.get("http://localhost:5000/getParams", params=payload)
        self.assertEqual(json.loads(r.text), json.loads('{ "Name": "Host1", "ID":"H1", "x": 10, "y":15}'))

    def testConnectivity(self):
        # Create a little topology
        self.assertEqual(self.AddNode('Switches'), 'S1')
        payload = {'id' : 'S1', 'config' : '{ "Name" : "Switch1", "ID" : "S1", "State" : true, "x": 10, "y":15, "DPID" : 1 }' }
        r = requests.post("http://localhost:5000/postParams", data=payload)
        self.assertEqual(r.text, 'success')
        self.assertEqual(self.AddNode('Hosts'), 'H1')
        self.assertEqual(self.AddLink('S1', 'H1'), 'success')
        self.assertEqual(self.AddNode('Hosts'), 'H2')
        self.assertEqual(self.AddLink('H2', 'S1'), 'success')
        # Try pinging
        time.sleep(1)
        result = self.Ping('H1', 'H2')
        with open('controller.log', 'r') as f:
            content = f.read()
            print content
            f.close()
        self.assertTrue(result.find('100% packet loss') == -1)

    def AddLink(self, node1, node2):
        payload = {'firstId' : node1, 'secondId' : node2}
        r = requests.post("http://localhost:5000/postAddLink", data=payload)
        return r.text

    def AddNode(self, type):
        payload = {'type' : type, 'x': 10, 'y':15}
        r = requests.post("http://localhost:5000/postAddNode", data=payload)
        return r.text

    def Ping(self, sender, receiver):
        payload = {'sender' : sender, 'receiver' : receiver}
        r = requests.get("http://localhost:5000/getPing", params=payload)
        return r.text

    def tearDown(self):
        payload = {'param' : 'clear'}
        requests.post( "http://localhost:5000/shutdown", data=payload )

        
if __name__ == '__main__':
    unittest.main()

