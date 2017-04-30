import unittest
import sys
import os.path
import json
sys.path.append(os.path.dirname(__file__)+"../")
from Builder import app
import requests
from threading import Thread
os.chdir('..')

class builderTest(unittest.TestCase):
    def setUp(self):
        self.th = Thread(target = app.run, args = ('0.0.0.0',))
        self.th.start()

    def testGetIndex(self):
        r = requests.get("http://localhost:5000/")
        f = open('static/index.html')
        data = f.read()
        self.assertEqual(r.text, data)

    def testGetSavedTopo(self):
        r = requests.get("http://localhost:5000/getSavedTopo")
        f = open('config.json')
        data = f.read()
        a = json.loads(r.text)
        b = json.loads(data)
        self.assertEqual(a, b)
        os.remove('config.json')
        r = requests.get("http://localhost:5000/getSavedTopo")
        a = json.loads(r.text)
        b = {}
        self.assertEqual(a, b)

    def testGetParams(self):
        payload = {'id': 'S1'}
        r = requests.get("http://localhost:5000/getParams", params=payload)
        self.assertEqual(r.text, 'S1')

    def testGetPing(self):
        payload = {'sender' : 'H1', 'receiver' : 'H2'}
        r = requests.get("http://localhost:5000/getPing", params=payload)
        self.assertEqual(r.text, 'ping success')

    def testPostParams(self):
        #add node
        payload = {'type' : 'host'}
        r = requests.post("http://localhost:5000/postAddNode", data=payload)
        self.assertEqual(r.text, 'H1')
        #test change node params
        payload = {'id' : 'H1', 'config' : '{ "Name" : "Host1", "ID" : "H1", "State" : false }' }
        r = requests.post("http://localhost:5000/postParams", data=payload)
        self.assertEqual(r.text, 'success')

    def testPostAddNode(self):
        payload = {'type' : 'host'}
        r = requests.post("http://localhost:5000/postAddNode", data=payload)
        self.assertEqual(r.text, 'H1')

    def testPostDelNode(self):
        #add node
        payload = {'type' : 'host'}
        r = requests.post("http://localhost:5000/postAddNode", data=payload)
        self.assertEqual(r.text, 'H1')
        #test node delete
        payload = {'id' : 'H1'}
        r = requests.post("http://localhost:5000/postDelNode", data=payload)
        self.assertEqual(r.text, 'success')

    def testPostAddLink(self):
        payload = {'firstId' : 'H1', 'secondId' : 'H2' }
        r = requests.post("http://localhost:5000/postAddLink", data=payload)
        self.assertEqual(r.text, 'success')

    def testPostDelLink(self):
        payload = {'firstId' : 'H1', 'secondId' : 'H2' }
        r = requests.post("http://localhost:5000/postDelLink", data=payload)
        self.assertEqual(r.text, 'success')    
    
    def testPostSaveTopo(self):
        # Save topo
        payload = {'config' : '{"Switches" : [{"ID" : "S1", "Name":"S2"}]}' }
        r = requests.post("http://localhost:5000/postSaveTopo", data=payload)
        self.assertEqual(r.text, 'success')  

        # Check if it was really saved 
        r = requests.get("http://localhost:5000/getSavedTopo")
        f = open('config.json', 'r')
        data = f.read()
        a = json.loads(r.text)
        b = json.loads(data)
        self.assertEqual(a, b)
    
    def tearDown(self):
        requests.post( "http://localhost:5000/shutdown" )
        self.th.join()

if __name__ == '__main__':
    unittest.main()
