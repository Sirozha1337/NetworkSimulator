#!/usr/bin/python

from __future__ import print_function

import os
import json
from mininet.net import Mininet
from mininet.link import Link

class Topology( Mininet ):
    # Generates ID for a new node of passed type    
    def generateId(self, type):
        newid = 1
        newtype = type[0].upper()
        for node in self:
                if node.startswith(newtype):
                    newid += 1
        return newtype + str(newid)

    # Adds node of passed type to the topology
    # Supported types - switch, host
    def addNode(self, type):
        newid = self.generateId(type)
        if type == 'switch':
            # Will be replaced on integration phase addSwitch( newid, cls=Switch, dpid=int(newid[1:]) )
            self.addSwitch( newid )
        elif type == 'host':
            # Will be replaced on integration phase
            self.addHost( newid )
        return newid

    # Removes node with passed id from topology
    def delNode(self, id):
        node = self.get(id)
        nodes = ( self.hosts if node in self.hosts else
                      ( self.switches if node in self.switches else
                        ( self.controllers if node in self.controllers else
                          [] ) ) )

        # Remove all links
        for link in self.links:
            if link.intf1.node == node:
                self.delLink(id, link.intf2.node.name)
            elif link.intf2.node == node:
                self.delLink(link.intf1.node.name, id)

        node.terminate()
        nodes.remove( node )

        del self.nameToNode[ node.name ]
    
    # Creates a link between two nodes with firstId and secondId
    # Calls node functions to update their interface configuration
    def addLink(self, firstId, secondId):
        # Get node objects
        node1 = self.get(firstId)
        node2 = self.get(secondId)
        
        link = [ link for link in self.links
                if (node1, node2) in (
                (link.intf1.node, link.intf2.node),
                (link.intf2.node, link.intf1.node) 
                ) ]

        if len(link) > 0:
            return 'error'

        # Generate names for interfaces
        iName1 = firstId + '-' + secondId
        iName2 = secondId + '-' + firstId

        # Create link
        link = Link(node1, node2, intfName1 = iName1, intfName2 = iName2)
        
        # This will be used when integrating with Host and Switch
        # For configuration file update
        #node1.addInterface(iName1)
        #node2.addInterface(iName2)
            
        # Read config file
        with open('config.json', 'r') as f:
            data = json.load(f)
    
        # Add link to config
        try:
            data['Links'].append([firstId, secondId])
        except(KeyError):
            data['Links'] = []
            data['Links'].append([firstId, secondId])
            pass

        # Write config file
        with open('config.json', 'w') as f:
            f.truncate(0)
            json.dump(data, f)

        self.links.append(link)
        return 'success'   

    def delLink(self, firstId, secondId):
        # Get node objects
        node1 = self.get(firstId)
        node2 = self.get(secondId)
        
        link = [ link for link in self.links
                if (node1, node2) in (
                (link.intf1.node, link.intf2.node),
                (link.intf2.node, link.intf1.node) 
                ) ][0] 

        link.delete()
        self.links.remove(link)
        # Read config file
        with open('config.json', 'r') as f:
            data = json.load(f)
    
        # Remove link from config
        try:
            data['Links'].remove([firstId, secondId])
        except(KeyError):
            data['Links'] = []
            data['Links'].remove([firstId, secondId])
            pass

        # Write config file
        with open('config.json', 'w') as f:
            f.truncate(0)
            json.dump(data, f)
    
    # Get params of a node with specified id
    def getParams(self, id):
        return self.get(id).getParams()

    # Set params of a node with specified id
    def setParams(self, id, config):
        return self.get(id).setParams(config)

    # Start ping command on a firstId node  
    # with IP from a secondId node
    def ping(self, firstId, secondId):
        return self.get(firstId).ping(self.get(secondId).IP)
