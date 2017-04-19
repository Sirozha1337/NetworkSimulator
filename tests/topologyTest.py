import unittest
import sys
import os.path
import json
sys.path.append(os.path.dirname(__file__)+"../")
from classes.Topology import Topology
os.chdir('..')

class topologyTest(unittest.TestCase):
    def setUp(self):
        self.topo = Topology()
        self.topo.start()

    def test_generateId(self):
        self.assertEqual(self.topo.generateId('switch'), 'S1')
        self.assertEqual(self.topo.generateId('host'), 'H1')

    def test_addHost(self):
        self.assertEqual(self.topo.addNode('host'), 'H1')
        self.assertEqual(self.topo.addNode('host'), 'H2')

    def test_addSwitch(self):
        self.assertEqual(self.topo.addNode('switch'), 'S1')
        self.assertEqual(self.topo.addNode('switch'), 'S2')

    def test_delNode(self):
        self.assertEqual(self.topo.addNode('switch'), 'S1')
        self.topo.delNode('S1')
        with self.assertRaises(KeyError):
            self.topo['S1']
        
    
    def tearDown(self):
        self.topo.stop()
if __name__ == '__main__':
    unittest.main()

