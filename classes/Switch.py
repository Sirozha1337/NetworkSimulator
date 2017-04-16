#!/usr/bin/python

from __future__ import print_function
import json
from mininet.node import UserSwitch

class Switch( UserSwitch ):
    # Initializes the object and writes initial config to file
    def __init__(self, name, dpid):
        UserSwitch.__init__( self, name, dpid )
        config = { }        
        config['ID'] = name
        config['DPID'] = dpid
        config['Name'] = name
        config['State'] = False
        with open('config.json', 'r') as f:
            data = json.load(f)
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
    
