#!/usr/bin/python

from __future__ import print_function

import os
import json
from mininet.node import ( Node, Host, OVSKernelSwitch, DefaultController,
                           Controller )
from mininet.net import Mininet
from mininet.link import Link, Intf
from Switch import Switch
from Controller import Controller
from Host import Host

class Topology( Mininet ):
    def __init__( self, topo=None, controller=Controller ):
        Mininet.__init__(self, topo=None, controller=None)
        Mininet.addController(self, name='c0', ip='127.0.0.1', controller=Controller)
        self.build()
        try:
            f = open('config.json', 'r')
            config = json.load(f)
            f.close()
            f = open('config.json', 'w')
            empty = {}
            json.dump(empty, f)
            f.close()
            if 'Switches' in config.keys():
                for sw in config['Switches']:
                    print('addswitch')
                    print(json.dumps(sw))
                    self.addSwitch( sw['ID'], cls=Switch, x=sw['x'], y=sw['y'] )
                    self[sw['ID']].start(self.controllers)
            
            if 'Hosts' in config.keys():
                for host in config['Hosts']:
                    print('addhost')
                    print(json.dumps(host))
                    self.addHost( host['ID'], cls=Host, x=host['x'], y=host['y'] )

            if 'Links' in config.keys():
                for link in config['Links']:
                    self.addLink( link[0], link[1] )

            if 'Hosts' in config.keys():
                for host, hconf in zip(self.hosts, config['Hosts']):
                    print('setParams')
                    print(json.dumps(hconf))
                    host.setParams(hconf)

            if 'Switches' in config.keys():
                print(str(zip(self.switches, config['Switches'])))
                for sw, sconf in zip(self.switches, config['Switches']):
                    print('setParams')
                    print(json.dumps(sconf))
                    sw.setParams(sconf)
                    
        except:
            pass            

    # Generates ID for a new node of passed type    
    def generateId(self, type):
        newid = 1
        newtype = type[0].upper()
        for node in self:
                if node.startswith(newtype):
                    if newid <= int(node[1:]):
                        newid = int(node[1:]) + 1
        return newtype + str(newid)

    # Adds node of passed type to the topology
    # Supported types - switch, host
    def addNode(self, type, x, y):
        newid = self.generateId(type)
        if type == 'switch':
            # Will be replaced on integration phase addSwitch( newid, cls=Switch, dpid=int(newid[1:]) )
            self.addSwitch( newid, cls=Switch, x=x, y=y )
            self[newid].start(self.controllers)
        elif type == 'host':
            # Will be replaced on integration phase
            self.addHost( newid, cls=Host, x=x, y=y )
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
            if link.intf1.node == node and id in self.nameToNode.keys():
                self.delLink(id, link.intf2.node.name)
            elif link.intf2.node == node and id in self.nameToNode.keys():
                self.delLink(link.intf1.node.name, id)
        
        node.destroy()
        node.terminate()
        nodes.remove( node )

        del self.nameToNode[ node.name ]
        return 'success'
    
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
        #link = Link(node1, node2, intfName1 = iName1, intfName2 = iName2)
        Mininet.addLink(self, node1=node1, node2=node2, intfName1 = iName1, intfName2 = iName2)
        # Update config with interfaces
        if node1.name.startswith('S'): 
            node1.start(self.controllers)
        if node2.name.startswith('S'):
            node2.start(self.controllers)
        node1.addInterface(iName1)  
        node2.addInterface(iName2)
        # Read config file
        with open('config.json', 'r') as f:
            data = json.load(f)
    
        # Add link to config
        try:
            data['Links'].append([firstId, secondId])
        except(KeyError):
            data['Links'] = []
            data['Links'].append([firstId, secondId])
            print('KeyError')
            pass

        # Write config file
        with open('config.json', 'w') as f:
            f.truncate(0)
            json.dump(data, f)

        try:
            self['c0'].configChanged()
        except:
            pass

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

        node1.delInterface(firstId+'-'+secondId);
        node2.delInterface(secondId+'-'+firstId);
        # Read config file
        with open('config.json', 'r') as f:
            data = json.load(f)

        # Remove link from config
        try:
            data['Links'].remove([firstId, secondId])
        except(KeyError):
            pass

        # Write config file
        with open('config.json', 'w') as f:
            f.truncate(0)
            json.dump(data, f)
        return 'success'
    
    # Get params of a node with specified id
    def getParams(self, id):
        return self.get(id).getParams()

    # Set params of a node with specified id
    def setParams(self, id, config):
        return self.get(id).setParams(config)

    # Start ping command on a firstId node  
    # with IP from a secondId node
    def ping(self, firstId, secondId):
        return self.get(firstId).ping(self.get(secondId).IP())
