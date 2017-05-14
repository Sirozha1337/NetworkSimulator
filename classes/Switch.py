#!/usr/bin/python

from __future__ import print_function
import json
from mininet.node import OVSSwitch, OVSKernelSwitch

class Switch( OVSKernelSwitch ):
    # Initializes the object and writes initial config to file
    def __init__(self, name, x, y, failMode='secure', datapath='kernel', **params):
        #self.listenPort = 6633
        self.dpid = int(name[1:])
        OVSKernelSwitch.__init__( self, name, failMode=failMode, datapath=datapath,**params)
        config = { }        
        config['ID'] = name
        config['DPID'] = int(name[1:])
        config['Name'] = name
        config['State'] = False
        config['x'] = float(x)
        config['y'] = float(y)
        with open('config.json', 'r') as f:
            data = json.load(f)
        try:
            data['Switches'].append(config)
        except KeyError:
            data['Switches'] = []
            data['Switches'].append(config)
        with open('config.json', 'w') as f:
            json.dump(data, f)

    # Removes switch entry from config 
    def destroy(self):
        with open('config.json', 'r') as f:
            data = json.load(f)
        for switch in data['Switches']:
            if switch['ID'] == self.name:
                data['Switches'].remove(switch)
        with open('config.json', 'w') as f:
            json.dump(data, f)

    # Returns parameters of a switch
    def getParams(self):
        with open('config.json', 'r') as f:
            data = json.load(f)
        for switch in data['Switches']:
            if switch['ID'] == self.name:
                return json.dumps(switch)
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

        self.cmd('ip link delete ' + name)

        n = [ n for n in data['Switches'] if n['ID'] == self.name ][0]

        n['interfaces'] = [i for i in n['interfaces'] if i.get('Name') != name]
        f = open('config.json', 'w')
        json.dump(data, f)
        f.close()

    # Sets the parameters and rewrites config
    def setParams(self, config):
        with open('config.json', 'r') as f:
            data = json.load(f)
        for index, switch in enumerate(data['Switches'], start=0):
            if switch['ID'] == self.name:
                data['Switches'][index] = config
                with open('config.json', 'w') as f:
                    f.truncate(0)
                    json.dump(data, f)
                return 'success'
        data['Switches'].append(config)
        with open('config.json', 'w') as f:
                        f.truncate(0)
                        json.dump(data, f)
        return 'success'
    
