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
        config['x'] = float(x)
        config['y'] = float(y)
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

    # Removes interface entry from config file
    def delInterface(self, name):
        f = open('config.json', 'r')
        data = json.load(f)
        f.close()

        try:
            port = self.ports.get( self.nameToIntf[ name ] )
            if port is not None:
                del self.intfs[ port ]
                del self.ports[ self.nameToIntf[ name ] ]
                del self.nameToIntf[ name ]
        except:
            pass

        for i, host in zip(range(len(data['Hosts'])), data['Hosts']):
            if host['ID'] == self.name:
                data['Hosts'][i]['interfaces'] = [a for a in data['Hosts'][i]['interfaces'] if a['Name'] != name]

        f = open('config.json', 'w')
        json.dump(data, f)
        f.close()

    # Sets the parameters and rewrites config
    def setParams(self, config):
        # read config file
        f = open('config.json', 'r')
        data = json.load(f)
        f.close()

        # set interface configuration
        if 'interfaces' in config.keys() and config['interfaces'][0]:
            mask = 0
            for number in str(config['interfaces'][0]['Mask']).split('.'):
                block = format(int(number), 'b')
                for letter in block:
                    mask += int(letter)
            try:
                self.setIP(config['interfaces'][0]['IP'], mask)
                self.setMAC(config['interfaces'][0]['MAC'])
            except:
                return 'error'

        # write new config to file
        f = open('config.json', 'w')
        for index, host in enumerate(data['Hosts'], start=0):
            if host['ID'] == self.name:
                data['Hosts'][index] = config
                json.dump(data, f)
                f.close()
                return 'success'

        return 'error'

    def ping(self, ip):
        return self.cmd('ping -c 5 ' + ip)

