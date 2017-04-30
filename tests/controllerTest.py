import unittest
import sys
import os.path
import json
sys.path.append(os.path.dirname(__file__)+"../")
from classes.Controller import Controller
from mininet.net import Mininet
from mininet.topo import LinearTopo
os.chdir('..')

class controllerTest(unittest.TestCase):
    def setUp(self):
        self.net = Mininet( topo=LinearTopo(k=1, n=2), controller=Controller )

    def testSameVlan(self):
        with open('config.json', 'w') as f:
            f.write('{"Switches": [{"Name" : "S1","ID" : "S1","DPID" : 1,"interfaces" :[{"Name" : "S1-H1","VLAN ID" : 10,"VLAN TYPE":"access"},{"Name" : "S1-H2","VLAN ID" : 10,"VLAN TYPE" : "access" } ], "State":false}]}')
            f.close()
        self.net.start()
        result = self.net['h1s1'].cmd('ping -c 5 ' + str(self.net['h2s1'].IP()))
        self.assertTrue(result.find('Unreachable') == -1)

    def testDifferentVlan(self):
        with open('config.json', 'w') as f:
            f.write('{"Switches": [{"Name" : "S1","ID" : "S1","DPID" : 1,"interfaces" :[{"Name" : "S1-H1","VLAN ID" : 11,"VLAN TYPE":"access"},{"Name" : "S1-H2","VLAN ID" : 10,"VLAN TYPE" : "access" } ], "State":false}]}')
            f.close()
        self.net.start()
        result = self.net['h1s1'].cmd('ping -c 5 ' + str(self.net['h2s1'].IP()))
        self.assertTrue(result.find('Unreachable') != -1)
    
    def tearDown(self):
        self.net.stop()

if __name__ == '__main__':
    unittest.main()

