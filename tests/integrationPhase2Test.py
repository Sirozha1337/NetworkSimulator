import unittest
import sys
import os.path
import os
import json
import time
sys.path.append(os.path.dirname(__file__)+"../")
from classes.Topology import Topology
from classes.Switch import Switch
from classes.Controller import Controller
from mininet.cli import CLI
os.chdir('..')

class integrationPhase2Test(unittest.TestCase):
    def setUp(self):
        self.topo = Topology(topo=None, controller=Controller)
        self.topo.start()

    def testConnectivity(self):
        # Create a little topology
        self.assertEqual(self.topo.addNode('switch'), 'S1')
        self.assertEqual(self.topo.addNode('host'), 'H1')
        self.assertEqual(self.topo.addLink('S1', 'H1'), 'success')
        self.assertEqual(self.topo.addNode('host'), 'H2')
        self.assertEqual(self.topo.addLink('S1', 'H2'), 'success')
        # Try pinging
        result = self.topo['H1'].cmd('ping -c 5 ' + str(self.topo['H2'].IP()))
        self.assertTrue(result.find('Unreachable') == -1)
        # Change configuration
        self.topo['S1'].setParams('{"Name" : "S1","ID" : "S1","DPID" : 1,"interfaces" :[{"Name" : "S1-H1","VLAN ID" : 12,"VLAN TYPE":"access"},{"Name" : "S1-H2","VLAN ID" : 10,"VLAN TYPE" : "access" }]}')
        # Notify controller
        self.topo['c0'].configChanged()
        # Wait a bit
        time.sleep(10)
        # Try pinging
        result = self.topo['H1'].cmd('ping -c 5 ' + str(self.topo['H2'].IP()))
        print result
        self.assertTrue(result.find('100% packet loss') != -1)

    def tearDown(self):
        for node in self.topo:
            if node.startswith('S') or node.startswith('H'):
                self.topo.delNode(node)
        self.topo.stop()
'''
    def testAddSwitch(self):
        self.assertEqual(self.topo.addNode('switch'), 'S1')
        a = json.loads(self.topo['S1'].getParams())
        b = json.loads('{"State": false, "DPID": 1, "Name": "S1", "ID":"S1"}')        
        self.assertEqual(a, b)

    def testDelNode(self):
        self.assertEqual(self.topo.addNode('switch'), 'S1')
        self.topo.delNode('S1')
        with self.assertRaises(KeyError):
            self.topo['S1']

    def testAddLink(self):    
        self.assertEqual(self.topo.addNode('switch'), 'S1')
        self.assertEqual(self.topo.addNode('switch'), 'S2')
        self.assertEqual(self.topo.addLink('S1', 'S2'), 'success')
        

    def testDelLink(self):
        self.assertEqual(self.topo.addNode('switch'), 'S1')
        self.assertEqual(self.topo.addNode('switch'), 'S2')
        self.assertEqual(self.topo.addLink('S1', 'S2'), 'success')
        self.topo.delLink('S1', 'S2')
        self.assertEqual(len(self.topo.links), 0)       
    
    def testConnectivity(self):
        self.assertEqual(self.topo.addNode('switch'), 'S1')
        self.assertEqual(self.topo.addNode('host'), 'H1')
        self.assertEqual(self.topo.addNode('host'), 'H2')
        self.assertEqual(self.topo.addLink('S1', 'H1'), 'success')
        self.assertEqual(self.topo.addLink('S1', 'H2'), 'success')
        print self.topo['H1'].cmd('ping -c 5 ' + str(self.topo['H2'].IP()))
        print self.topo.items()
        print self.topo['S1'].intfList()
        print self.topo.controllers
        print self.topo['S1'].connected()
        print self.topo['S1'].cmd('ovs-vsctl show')
'''
if __name__ == '__main__':
    unittest.main()

