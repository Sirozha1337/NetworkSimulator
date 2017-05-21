#!/usr/bin/python

from __future__ import print_function
import json
from mininet.node import Host as MHost
import string

class Router( MHost ):
    def __init__( self, name, inNamespace = True, **params ):
        MHost.__init__(self, name, inNamespace = True, **params)
        self.nodeType = 'Routers'
        #Enable forwarding on the router
        self.cmd( 'sysctl net.ipv4.ip_forward=1' )

    def terminate( self ):
        self.cmd( 'sysctl net.ipv4.ip_forward=0' )
        MHost.terminate(self)

    # Applies the parameters 
    def applyParams(self, config):
      
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
                except:
                    return 'Error:\nIncorrect IP address or mask'
                try:
                    self.setMAC( interface['MAC'],
                                intf = thisInterface )
                except:
                    return 'Error:\nIncorrect MAC address'
        
        if 'Routing' in config.keys():
            self.cmd('ip route del 0/0')
            for route in config['Routing']:
                result = self.cmd('route add -net ' + route['Destination'] + ' netmask ' + route['Mask'] + ' dev ' + route['Interface'])
                if result != "":
                    return 'Error:\n' + result.split('\n')[0]
        
        return 'success'
