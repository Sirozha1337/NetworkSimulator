#!/usr/bin/python

from __future__ import print_function
import json
from mininet.node import OVSSwitch

class Switch( OVSSwitch ):
    # Initializes the object and writes initial config to file
    def __init__(self, name, failMode='secure', datapath='user', **params):
        self.dpid = int(name[1:])
        self.nodeType = 'Switches'
        OVSSwitch.__init__( self, name, failMode=failMode, datapath=datapath,**params)

    # Applies switch params using ovs-vsctl 
    def applyParams(self, config):
        # Restart switch, so it would discover its new interfaces
        self.start([])
        
        # Check if switch is in turned on state
        if 'State' in config.keys() and config['State']:
            self.failMode = 'standalone'
            self.vsctl('set-fail-mode', self.name, 'standalone')
            self.vsctl('set-controller ', self.name)
        else:
            self.failMode = 'secure'
            self.vsctl('set-fail-mode', self.name, 'secure')
        
        # Apply vlan config to interfaces
        if 'interfaces' in config.keys():
            for interface in config['interfaces']:
                vlan_mode = interface['VLAN TYPE'] if interface['VLAN TYPE'] == 'access' else 'native-tagged'
                self.vsctl('set port', interface['Name'], 'tag=' + str(interface['VLAN ID']), 'vlan_mode=' + vlan_mode)
        print(self.vsctl('show'))
        return 'success'
    
