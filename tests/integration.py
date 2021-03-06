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

class integration(unittest.TestCase):
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

    def testSwitch(self):
        # Create a little topology
        self.assertEqual(self.AddNode('Switches'), 'S1')
        payload = {'id' : 'S1', 'config' : '{ "Name" : "Switch1", "ID" : "S1", "State" : true, "x": 10, "y":15, "DPID" : 1 }' }
        r = requests.post("http://localhost:5000/postParams", data=payload)
        self.assertEqual(r.text, 'success')
        self.assertEqual(self.AddNode('Hosts'), 'H1')
        self.assertEqual(self.AddLink('S1', 'H1'), 'success')
        self.assertEqual(self.AddNode('Hosts'), 'H2')
        self.assertEqual(self.AddLink('H2', 'S1'), 'success')
        # Try ping
        result = self.Ping('H1', 'H2')
        self.assertTrue(result.find('100% packet loss') == -1 and result.find('Network is unreachable') == -1)
    
    def testAddDeleteLink(self):
        self.assertEqual(self.AddNode('Switches'), 'S1')
        payload = {'id' : 'S1', 'config' : '{ "Name" : "Switch1", "ID" : "S1", "State" : true, "x": 10, "y":15, "DPID" : 1 }' }
        r = requests.post("http://localhost:5000/postParams", data=payload)
        self.assertEqual(r.text, 'success')
        self.assertEqual(self.AddNode('Hosts'), 'H1')
        self.assertEqual(self.AddLink('S1', 'H1'), 'success')
        self.assertEqual(self.AddNode('Hosts'), 'H2')
        self.assertEqual(self.AddLink('H2', 'S1'), 'success')
        self.assertEqual(self.DelLink('H2', 'S1'), 'success')

        # Try ping
        result = self.Ping('H2', 'H1')
        self.assertTrue(result.find('100% packet loss') != -1 or result.find('Network is unreachable') != -1)

        # Add another switch and host and connect H2 to this network
        self.assertEqual(self.AddNode('Switches'), 'S2')
        payload = {'id' : 'S2', 'config' : '{ "Name": "Switch2", "ID": "S2", "State": true, "x": 10, "y": 15, "DPID": 2 }' }
        r = requests.post("http://localhost:5000/postParams", data=payload)
        self.assertEqual(r.text, 'success')

        self.assertEqual(self.AddNode('Hosts'), 'H3')
        self.assertEqual(self.AddLink('S2', 'H3'), 'success')
        self.assertEqual(self.AddLink('H2', 'S2'), 'success')

        # Try ping
        result = self.Ping('H2', 'H3')
        self.assertTrue(result.find('100% packet loss') == -1 and result.find('Network is unreachable') == -1)
        result = self.Ping('H2', 'H1')
        self.assertTrue(result.find('100% packet loss') != -1 or result.find('Network is unreachable') != -1)

        # Remove link between S2 and H2 and move H2 to the previous network
        self.assertEqual(self.DelLink('H2', 'S2'), 'success')
        self.assertEqual(self.AddLink('H2', 'S1'), 'success')
        
        # Try ping
        result = self.Ping('H2', 'H1')
        self.assertTrue(result.find('100% packet loss') == -1 and result.find('Network is unreachable') == -1)
        

    def testAdvancedTopology(self):
        # Create topo
        self.assertEqual(self.AddNode('Switches'), 'S1')
        self.assertEqual(self.AddNode('Switches'), 'S2')
        self.assertEqual(self.AddNode('Hosts'), 'H1')
        self.assertEqual(self.AddNode('Hosts'), 'H2')
        self.assertEqual(self.AddNode('Routers'), 'R1')
        self.assertEqual(self.AddLink('H1', 'S1'), 'success')
        self.assertEqual(self.AddLink('H2', 'S2'), 'success')
        self.assertEqual(self.AddLink('R1', 'S1'), 'success')
        self.assertEqual(self.AddLink('R1', 'S2'), 'success')

        payload = { 'id' : 'H1', 'config' : '{ "Name" : "Host1", "ID" : "H1", "x": 10, "y":15, "interfaces": [{"IP": "10.0.0.1", "MAC": "d2:5a:2c:c7:14:d0", "Mask": "255.0.0.0", "Name": "H1-S1", "Gateway": "10.0.0.3"}] }' }
        r = requests.post("http://localhost:5000/postParams", data=payload)
        self.assertEqual(r.text, 'success')

        payload = {'id' : 'H2', 'config' : '{ "Name" : "Host2", "ID" : "H2", "x": 10, "y":15, "interfaces": [{"IP": "192.168.0.1", "MAC": "2a:d7:3a:d5:2b:46", "Mask": "255.255.255.0", "Name": "H2-S2", "Gateway": "192.168.0.3"}] }' }
        r = requests.post("http://localhost:5000/postParams", data=payload)
        self.assertEqual(r.text, 'success')

        payload = {'id' : 'R1', 'config' : '{"Name": "R1", "interfaces": [{"IP": "10.0.0.3", "MAC": "d2:f2:b2:aa:18:db", "Mask": "255.0.0.0", "Name": "R1-S1"}, {"IP": "192.168.0.3", "MAC": "2a:d7:3a:d5:2b:49", "Mask": "255.255.255.0", "Name": "R1-S2"}], "Routing": [], "y": 176, "x": 268, "ID": "R1"}' }
        r = requests.post("http://localhost:5000/postParams", data=payload)
        self.assertEqual(r.text, 'success')

        payload = {'id' : 'S1', 'config' : '{ "Name" : "Switch1", "ID" : "S1", "State" : true, "x": 10, "y":15, "DPID" : 1, "interfaces": [{"Name": "S1-H1", "VLAN ID": 1, "VLAN TYPE": "access"}, {"Name": "S1-R1", "VLAN ID": 1, "VLAN TYPE": "access"}] }' }
        r = requests.post("http://localhost:5000/postParams", data=payload)
        self.assertEqual(r.text, 'success')

        payload = {'id' : 'S2', 'config' : '{ "Name" : "Switch2", "ID" : "S2", "State" : true, "x": 10, "y":15, "DPID" : 1, "interfaces": [{"Name": "S2-H2", "VLAN ID": 1, "VLAN TYPE": "access"}, {"Name": "S2-R1", "VLAN ID": 1, "VLAN TYPE": "access"} ] }' }
        r = requests.post("http://localhost:5000/postParams", data=payload)
        self.assertEqual(r.text, 'success')

        result = self.Ping('H1', 'H2')
        self.assertTrue(result.find('100% packet loss') == -1 and result.find('Network is unreachable') == -1)
                
        

    def testRouter(self):
        # Create a little topology
        self.assertEqual(self.AddNode('Routers'), 'R1')
        self.assertEqual(self.AddNode('Hosts'), 'H1')
        self.assertEqual(self.AddLink('R1', 'H1'), 'success')
        self.assertEqual(self.AddNode('Hosts'), 'H2')
        self.assertEqual(self.AddLink('H2', 'R1'), 'success')
        payload = {'id' : 'H1', 'config' : '{ "Name" : "Host1", "ID" : "H1", "x": 10, "y":15, "interfaces": [{"IP": "10.0.0.1", "MAC": "d2:5a:2c:c7:14:d0", "Mask": "255.0.0.0", "Name": "H1-R1", "Gateway": "10.0.0.3"}] }' }
        r = requests.post("http://localhost:5000/postParams", data=payload)
        payload = {'id' : 'H2', 'config' : '{ "y": 78, "x": 368, "interfaces": [{"IP": "192.168.0.1", "MAC": "2a:d7:3a:d5:2b:46", "Mask": "255.0.0.0", "Name": "H2-R1", "Gateway": "192.168.0.3"}], "Name": "H2", "ID": "H2" }' }
        self.assertEqual(r.text, 'success')
        r = requests.post("http://localhost:5000/postParams", data=payload)
        self.assertEqual(r.text, 'success')
        payload = {'id' : 'R1', 'config' : '{"Name": "R1", "interfaces": [{"IP": "10.0.0.3", "MAC": "d2:f2:b2:aa:18:db", "Mask": "255.0.0.0", "Name": "R1-H1"}, {"IP": "192.168.0.3", "MAC": "d2:f2:b2:aa:18:db", "Mask": "255.255.255.0", "Name": "R1-H2"}], "Routing": [], "y": 176, "x": 268, "ID": "R1"}' }
        r = requests.post("http://localhost:5000/postParams", data=payload)
        self.assertEqual(r.text, 'success')
        result = self.Ping('H1', 'H2')
        self.assertTrue(result.find('100% packet loss') == -1 and result.find('Network is unreachable') == -1)

    def AddLink(self, node1, node2):
        payload = {'firstId' : node1, 'secondId' : node2}
        r = requests.post("http://localhost:5000/postAddLink", data=payload)
        return r.text

    def DelLink(self, node1, node2):
        payload = {'firstId' : node1, 'secondId' : node2}
        r = requests.post("http://localhost:5000/postDelLink", data=payload)
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

