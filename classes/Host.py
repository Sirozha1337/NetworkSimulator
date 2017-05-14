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

    # Sets the parameters and rewrites config
    def setParams(self, config):

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

        return 'success'

    def ping(self, ip):
        return self.cmd('ping -c 5 ' + ip)

