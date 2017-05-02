#!/usr/bin/python

from __future__ import print_function
import json
from mininet.node import Host as MHost
import string

class Host( MHost ):
    # Initializes the object and writes initial config to file
    def __init__(self, name, x, y, inNamespace = True, **params):
        MHost.__init__( self, name, inNamespace = True,**params)
        config = { }        
        config['ID'] = name
        config['Name'] = name
        config['State'] = False
        config['x'] = int(x)
        config['y'] = int(y)
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
        interface['Mask'] = '255.0.0.0'
        interface['IP'] = '10.0.0.'+self.name[1:]
        self.setIP(interface['IP'], 8)
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
        if(config['interfaces'][0]):
            mask = 0
            for number in config['interfaces'][0]['Mask'].split('.'):
                block = format(int(number), 'b')
                for letter in block:
                    if letter == '1':
                        mask += 1
            try:
                self.setIP(config['interfaces'][0]['IP'], mask)
                self.setMAC(config['interfaces'][0]['MAC'])
            except:
                return 'error'
        for index, host in enumerate(data['Hosts'], start=0):
            if host['ID'] == self.name:
                data['Hosts'][index] = config
                with open('config.json', 'w') as f:
                    f.truncate(0)
                    json.dump(data, f)
                return 'success'
        data['Hosts'].append(config)
        with open('config.json', 'w') as f:
                        f.truncate(0)
                        json.dump(data, f)
        return 'success'

    def ping(self, ip):
        return self.cmd('ping -c 5 ' + ip)

