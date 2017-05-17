#!/usr/bin/python

from __future__ import print_function
import json
from mininet.node import Host as MHost
import string

class Host( MHost ):
    def __init__( self, name, inNamespace = True, **params ):
        MHost.__init__(self, name, inNamespace = True, **params)
        self.nodeType = 'Hosts'

    # Applies host configuration
    def applyParams(self, config):
        # set interface configuration
        if 'interfaces' in config.keys() and config['interfaces'][0]:
            mask = 0
            # Calculate mask
            for number in str(config['interfaces'][0]['Mask']).split('.'):
                block = format(int(number), 'b')
                for letter in block:
                    mask += int(letter)
            try:
                self.setIP(config['interfaces'][0]['IP'], mask)
                self.setMAC(config['interfaces'][0]['MAC'])
                self.cmd('route del default')
                self.cmd('route add default gw ' + config['interfaces'][0]['Gateway'])
            except:
                return 'error'

        return 'success'

    # Execute ping command
    def ping(self, ip):
        return self.cmd('ping -c 5 ' + ip)

