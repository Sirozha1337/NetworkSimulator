import unittest
import sys
import os.path
import json
sys.path.append(os.path.dirname(__file__)+"../")
from classes.Host import Host
os.chdir('..')

class HostTest(unittest.TestCase):
    def setUp(self):
        self.hosts = {}
        host1 = Host(name='H1')
        host2 = Host(name='H2')
        self.hosts['host1'] = host1
        self.hosts['host2'] = host2
    
    def testGet(self):
        a = json.loads(self.hosts['host1'].getParams())
        b = json.loads('{"State": false, "Name": "H1", "ID":"H1"}')
        self.assertEqual(a, b)
        a = json.loads(self.hosts['host2'].getParams())
        b = json.loads('{"State": false, "Name": "H2", "ID":"H2"}')
        self.assertEqual(a, b)

    def testSet(self):
        b = json.loads('{"State": false, "Name": "Host1", "ID":"H1"}')
        self.hosts['host1'].setParams(b)
        a = json.loads(self.hosts['host1'].getParams())
        self.assertEqual(a, b)
        b = json.loads('{"State": true, "Name": "Host2", "ID":"H2"}')
        self.hosts['host2'].setParams(b)
        a = json.loads(self.hosts['host2'].getParams())
        self.assertEqual(a, b)

    def testPing(self):
        self.hosts['host1'].linkTo(self.hosts['host2'])
        self.hosts['host1'].addInterface('H1-H2')
        result = self.hosts['host1'].ping('10.0.0.1')
        self.assertTrue(result.find('transmitted'))

    def tearDown(self):
        self.hosts['host1'].destroy()
        self.hosts['host2'].destroy()

if __name__ == '__main__':
    unittest.main()
