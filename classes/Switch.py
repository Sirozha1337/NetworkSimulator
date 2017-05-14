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
    
