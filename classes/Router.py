#!/usr/bin/python

from __future__ import print_function
import json
from mininet.node import Host as MHost
import string

class Router( MHost ):
    # Initializes the object and writes initial config to file
    def __init__(self, name, x, y, inNamespace = True, **params):
        MHost.__init__( self, name, inNamespace = True,**params)

    # Makes router out of mininet host
    def config( self, mac=None, ip=None,
                defaultRoute=None, lo='up', **_params ):
        if self.intfs:
            self.setParam( _params, 'setIP', ip='0.0.0.0' )
        r = Node.config( self, **_params )
        self.cmd('sysctl -w net.ipv4.ip_forward=1')
        return r

    # Sets the parameters and rewrites config
    def setParams(self, config):

        # Set interface configuration
        if 'interfaces' in config.keys():
            for interface in config['interfaces']:
                mask = 0
                for number in str(interface['Mask']).split('.'):
                    block = format(int(number), 'b')
                    for letter in block:
                        mask += int(letter)
                try:
                    thisInterface = self.intfList()[ self.intfNames().index(interface['Name']) ]
                    self.setIP( interface['IP'], mask, 
                                intf = thisInterface)
                    self.setMAC( interface['MAC'],
                                intf = thisInterface )
                except:
                    return 'error'

        return 'success'
