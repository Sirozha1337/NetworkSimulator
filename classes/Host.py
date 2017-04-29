#!/usr/bin/python

from __future__ import print_function
import json
from mininet.node import Host as MHost

class Host( MHost ):
    # Initializes the object and writes initial config to file
    def __init__(self, name, inNamespace = True, **params):
        MHost.__init__( self, name, inNamespace = True,**params)
        config = { }        
        config['ID'] = name
        config['Name'] = name
        config['State'] = False
        with open('config.json', 'r') as f:
            data = json.load(f)
        try:
            data['Hosts'].append(config)
        except KeyError:
            data['Hosts'] = []
            data['Hosts'].append(config)
        with open('config.json', 'w') as f:
            json.dump(data, f)

    # Removes host entry from config 
    def destroy(self):
        with open('config.json', 'r') as f:
            data = json.load(f)
        for host in data['Hosts']:
            if host['ID'] == self.name:
                data['Hosts'].remove(host)
        with open('config.json', 'w') as f:
            json.dump(data, f)

    # Returns parameters of a host
    def getParams(self):
        with open('config.json', 'r') as f:
            data = json.load(f)
        for host in data['Hosts']:
            if host['ID'] == self.name:
                return json.dumps(host)
        return json.dumps(None)
    
    # Creates an entry in config with default interface parameters
    def addInterface(self, name):
        with open('config.json', 'r') as f:
            data = json.load(f)
        n = [ n for n in data['Hosts'] if n['ID'] == self.name ][0]
        interface = {}
        interface['Name'] = name
        interface['IP'] = '10.0.0.'+self.name[1:]
        self.setIP(interface['IP'])
        interface['MAC'] = str(self.MAC())
        try:
            n['interfaces'].append(interface)
        except(KeyError):
            n['interfaces'] = []
            n['interfaces'].append(interface)
            pass
        with open('config.json', 'w') as f:
            f.truncate(0)
            json.dump(data, f)

    # Removes interface entry from config file
    def delInterface(self, name):
        with open('config.json', 'r') as f:
            data = json.load(f)
        n = [ n for n in data['Hosts'] if n['ID'] == self.name ][0]
        n['interfaces'] = [i for i in n['interfaces'] if i.get('Name') != name]
        with open('config.json', 'w') as f:
            f.truncate(0)
            json.dump(data, f)

    # Sets the parameters and rewrites config
    def setParams(self, config):
        with open('config.json', 'r') as f:
            data = json.load(f)
        a = json.loads(config)
        if a['interfaces']:
            self.setIP(a['interfaces'][0]['IP'])
            self.setMAC(a['interfaces'][0]['MAC'])
        for index, host in enumerate(data['Hosts'], start=0):
            if host['ID'] == self.name:
                data['Hosts'][index] = a
                with open('config.json', 'w') as f:
                    f.truncate(0)
                    json.dump(data, f)
                return 'success'
        data['Hosts'].append(config)
        with open('config.json', 'w') as f:
                        f.truncate(0)
                        json.dump(data, f)
        return 'success'
