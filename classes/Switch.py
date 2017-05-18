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
        r = self.cmd('ovs-vsctl show')
        print(r)

    def start(self, controllers):
        OVSSwitch.start(self, controllers)
        print('start')

    # Does nothing as the switch configuration depends on controller
    def applyParams(self, config):
        self.start([])
        print('applying switch params')
        if 'State' in config.keys() and config['State']:
            self.failMode = 'standalone'
            self.cmd('sudo ovs-vsctl set-fail-mode ' + self.name + ' standalone')
            self.cmd('sudo ovs-vsctl set-controller ' + self.name)
        else:
            self.failMode = 'secure'
            self.cmd('sudo ovs-vsctl set-fail-mode ' + self.name + ' secure')
        if 'interfaces' in config.keys():
            print('if')
            for interface in config['interfaces']:
                print('for')
                vlan_mode = interface['VLAN TYPE'] if interface['VLAN TYPE'] == 'access' else 'native-tagged'
                print(vlan_mode)
                r = self.cmd('sudo ovs-vsctl set port ' + interface['Name'] + ' tag=' + str(interface['VLAN ID']) + ' vlan_mode=' + vlan_mode)
                print(r)
                r = self.cmd('ovs-vsctl show')
                print(r)
        return 'success'
    
