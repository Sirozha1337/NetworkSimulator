import unittest
import sys
import os.path
import json
sys.path.append(os.path.dirname(__file__)+"../")
from classes.Switch import Switch
os.chdir('..')

class SwitchTest(unittest.TestCase):
    def setUp(self):
        self.switches = {}
        switch1 = Switch(name='S1', dpid='1')
        switch2 = Switch(name='S2', dpid='2')
        self.switches['switch1'] = switch1
        self.switches['switch2'] = switch2
    
    def testGet(self):
        a = json.loads(self.switches['switch1'].getParams())
        b = json.loads('{"State": false, "DPID": "1", "Name": "S1", "ID":"S1"}')
        self.assertEqual(a, b)
        a = json.loads(self.switches['switch2'].getParams())
        b = json.loads('{"State": false, "DPID": "2", "Name": "S2", "ID":"S2"}')
        self.assertEqual(a, b)

    def testSet(self):
        b = json.loads('{"State": false, "DPID": "1", "Name": "Switch1", "ID":"S1"}')
        self.switches['switch1'].setParams(b)
        a = json.loads(self.switches['switch1'].getParams())
        self.assertEqual(a, b)
        b = json.loads('{"State": true, "DPID": "2", "Name": "Switch2", "ID":"S2"}')
        self.switches['switch2'].setParams(b)
        a = json.loads(self.switches['switch2'].getParams())
        self.assertEqual(a, b)

    def tearDown(self):
        self.switches['switch1'].destroy()
        self.switches['switch2'].destroy()

if __name__ == '__main__':
    unittest.main()
