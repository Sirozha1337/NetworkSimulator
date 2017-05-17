#!/usr/bin/python

from __future__ import print_function
import json
from mininet.node import OVSSwitch, OVSKernelSwitch

class Switch( OVSKernelSwitch ):
    # Initializes the object and writes initial config to file
    def __init__(self, name, failMode='secure', datapath='kernel', **params):
        self.dpid = int(name[1:])
        self.nodeType = 'Switches'
        OVSKernelSwitch.__init__( self, name, failMode=failMode, datapath=datapath,**params)

    # Does nothing as the switch configuration depends on controller
    def applyParams(self, config):
        return 'success'
    
