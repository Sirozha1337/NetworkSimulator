import unittest
import sys
import os.path
import os
import json
import time
sys.path.append(os.path.dirname(__file__)+"../")
from Builder import app
import requests
from threading import Thread
os.chdir('..')

class integrationPhase3Test(unittest.TestCase):
    def setUp(self):
        os.spawnl(os.P_NOWAIT, '/usr/bin/python', 'python',  'Builder.py')
        time.sleep(10)

    def testPostAddNode(self):
        payload = {'type' : 'host'}
        r = requests.post("http://localhost:5000/postAddNode", data=payload)
        self.assertEqual(r.text, 'H1')
        payload = {'type' : 'switch'}
        r = requests.post("http://localhost:5000/postAddNode", data=payload)
        self.assertEqual(r.text, 'S1')

    def testGetParams(self):
        # Add switch
        payload = {'type' : 'switch'}
        r = requests.post("http://localhost:5000/postAddNode", data=payload)
        self.assertEqual(r.text, 'S1')
        # Get switch params
        payload = {'id': 'S1'}
        r = requests.get("http://localhost:5000/getParams", params=payload)
        self.assertEqual(json.loads(r.text), json.loads('{"State": false, "DPID": 1, "Name": "S1", "ID":"S1"}'))
        # Add host
        payload = {'type' : 'host'}
        r = requests.post("http://localhost:5000/postAddNode", data=payload)
        self.assertEqual(r.text, 'H1')
        # Get host params
        payload = {'id': 'H1'}
        r = requests.get("http://localhost:5000/getParams", params=payload)
        self.assertEqual(json.loads(r.text), json.loads('{"State": false, "Name": "H1", "ID":"H1"}'))

    def testSetParams(self):
        #add node
        payload = {'type' : 'host'}
        r = requests.post("http://localhost:5000/postAddNode", data=payload)
        self.assertEqual(r.text, 'H1')
        #test change node params
        payload = {'id' : 'H1', 'config' : '{ "Name" : "Host1", "ID" : "H1", "State" : false }' }
        r = requests.post("http://localhost:5000/postParams", data=payload)
        self.assertEqual(r.text, 'success')
        # Check if the parameters changed correctly
        payload = {'id': 'H1'}
        r = requests.get("http://localhost:5000/getParams", params=payload)
        self.assertEqual(json.loads(r.text), json.loads('{"State": false, "Name": "Host1", "ID":"H1"}'))

    def testConnectivity(self):
        # Create a little topology
        self.assertEqual(self.AddNode('switch'), 'S1')
        self.assertEqual(self.AddNode('host'), 'H1')
        self.assertEqual(self.AddLink('S1', 'H1'), 'success')
        self.assertEqual(self.AddNode('host'), 'H2')
        self.assertEqual(self.AddLink('S1', 'H2'), 'success')
        # Try pinging
        time.sleep(10)
        result = self.Ping('H1', 'H2')
        print result
        self.assertTrue(result.find('100% packet loss') == -1)
        
    def AddLink(self, node1, node2):
        payload = {'firstId' : node1, 'secondId' : node2}
        r = requests.post("http://localhost:5000/postAddLink", data=payload)
        return r.text

    def AddNode(self, type):
        payload = {'type' : type}
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

