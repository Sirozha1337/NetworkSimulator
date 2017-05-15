#!/usr/bin/python

from __future__ import print_function

import os
import json
from mininet.node import ( Node, Host, OVSKernelSwitch )
from mininet.net import Mininet
from mininet.link import Link, Intf
from Switch import Switch
from Controller import Controller
from Host import Host
from time import sleep

class Topology( Mininet ):
    def __init__( self, topo=None, controller=Controller ):
        Mininet.__init__(self, topo=None, controller=None)
        Mininet.addController(self, name='c0', ip='127.0.0.1', controller=Controller)
        self.build()
        try:
            f = open('config.json', 'r')
            config = json.load(f)
            f.close()

            if 'Switches' in config.keys():
                for sw in config['Switches']:
                    print('Adding switches')
                    self.addSwitch( sw['ID'], cls=Switch, x=sw['x'], y=sw['y'] )
                    self.nameToNode[sw['ID']].start(self.controllers)
            
            if 'Hosts' in config.keys():
                for host in config['Hosts']:
                    print('Adding hosts')
                    self.addHost( host['ID'], cls=Host, x=host['x'], y=host['y'] )

            if 'Links' in config.keys():
                for link in config['Links']:
                    print('Adding links')
                    self.addLink( link[0], link[1] )

            if 'Hosts' in config.keys():
                for host, hconf in zip(self.hosts, config['Hosts']):
                    print('Setting host parameters')
                    host.applyParams(hconf)

            if 'Switches' in config.keys():
                for sw, sconf in zip(self.switches, config['Switches']):
                    print('Setting switch parameters')
                    sw.applyParams(sconf)
                    
        except:
            pass            

    # Generates ID for a new node of passed type    
    def generateId(self, nodeType):
        newid = 1
        newtype = nodeType[0].upper()
        for node in self.nameToNode:
                if node.startswith(newtype):
                    if newid == int(node[1:]):
                        newid = int(node[1:]) + 1
        return newtype + str(newid)

    # Adds node of passed type to the topology
    # Supported types - Switches, Hosts, Routers
    def addNode(self, nodeType, x, y, newid=None):
        if newid is None:
            newid = self.generateId(nodeType)
            config = { }        
            config['ID'] = newid
            config['Name'] = newid
            if nodeType == 'Switches':
                config['State'] = False
                config['DPID'] = int(newid[1:])
            config['x'] = float(x)
            config['y'] = float(y)

            f = open('config.json', 'r')
            data = json.load(f)
            f.close()

            if nodeType in data.keys():
                data[nodeType].append(config)
            else:
                data[nodeType] = []
                data[nodeType].append(config)

            f = open('config.json', 'w')
            json.dump(data, f)
            f.close()

        if nodeType == 'Switches':
            self.addSwitch( newid, cls=Switch, x=x, y=y )
            self.nameToNode[newid].start(self.controllers)

        elif nodeType == 'Hosts':
            self.addHost( newid, cls=Host, x=x, y=y )

        elif nodeType == 'Routers':
            self.addHost( newid, cls=Router, x=x, y=y )

        return newid

    # Removes node with passed id from topology
    def delNode(self, id):
        node = self.nameToNode[id]

        if id.startswith('S'):
            nodes = ( self.switches )
            nodeType = "Switches"
        elif id.startswith('H'):
            nodes = ( self.hosts )
            nodeType = "Hosts"

        # Remove all links
        linksToRemove = []
        for link in self.links:
            if link.intf1.node == node and id in self.nameToNode.keys():
                linksToRemove.append(link)
            elif link.intf2.node == node and id in self.nameToNode.keys():
                linksToRemove.append(link)

        for link in linksToRemove:
            self.delLink(link.intf1.node.name, link.intf2.node.name)

        
        # Removes node entry from config 
        f = open('config.json', 'r')
        data = json.load(f)
        f.close()
        
        for nodeEntry in data[nodeType]:
            if nodeEntry['ID'] == id:
                data[nodeType].remove(nodeEntry)
        
        f = open('config.json', 'w')
        json.dump(data, f)
        f.close()

        node.terminate()
        nodes.remove( node )

        del self.nameToNode[ node.name ]
        return 'success'
    
    # Creates a link between two nodes with firstId and secondId
    # Calls node functions to update their interface configuration
    def addLink(self, firstId, secondId):
        # Get node objects
        node1 = self.nameToNode[firstId]
        node2 = self.nameToNode[secondId]
        
        link = self.getLinkBetweenNodes(node1, node2)

        if len(link) > 0:
            return 'error'

        # Generate names for interfaces
        iName1 = firstId + '-' + secondId
        iName2 = secondId + '-' + firstId

        # Create link
        Mininet.addLink(self, node1=node1, node2=node2, intfName1 = iName1, intfName2 = iName2)

        # add interfaces to config
        self.addInterface(node1, iName1)
        self.addInterface(node2, iName2)

        try:
            if node1.name.startswith('S'):
                node1.start(self.controllers)
            if node2.name.startswith('S'):
                node2.start(self.controllers)
            sleep(1)
            self.nameToNode['c0'].configChanged()

        except:
            pass

        return 'success'   
    
    def setLink(self, firstId, secondId):
        result = self.addLink(firstId, secondId)
        if result == 'success':
            # Read config file
            f = open('config.json', 'r')
            data = json.load(f)
            f.close()
        
            # Add link to config
            if 'Links' in data.keys():
                data['Links'].append([firstId, secondId])
            else:
                data['Links'] = []
                data['Links'].append([firstId, secondId])

            # Write config file
            f = open('config.json', 'w')
            json.dump(data, f)
            f.close()

        return result

    def getLinkBetweenNodes(self, node1, node2):
        return [ link for link in self.links
                if (node1, node2) in (
                (link.intf1.node, link.intf2.node),
                (link.intf2.node, link.intf1.node) 
                ) ] 

    # Delete interface entry from configuration file
    def deleteInterface(self, node, intfName):
        f = open('config.json', 'r')
        data = json.load(f)
        f.close()

        try:
            port = self.ports.get( node.nameToIntf[ intfName ] )
            if port is not None:
                del self.intfs[ port ]
                del self.ports[ self.nameToIntf[ intfName ] ]
                del self.nameToIntf[ intfName ]
        except:
            pass

        node.cmd('ip link delete ' + intfName)

        n = self.findConfigEntry(node, data)

        n['interfaces'] = [i for i in n['interfaces'] if i.get('Name') != intfName]

        f = open('config.json', 'w')
        json.dump(data, f)
        f.close()

    def nodeType(self, node):
        if node.name.startswith('S'):
            return 'Switches'
        elif node.name.startswith('H'):
            return 'Hosts'
        elif node.name.startswith('R'):
            return 'Routers'

    # returns config entry in data which represents the specified node
    def findConfigEntry(self, node, data):
        nodeType = self.nodeType(node)
        n = [ n for n in data[nodeType] if n['ID'] == node.name ][0]
        return n

    # Add interface entry in configuration file
    def addInterface(self, node, intfName):
        f = open('config.json', 'r')
        data = json.load(f)
        f.close()
        interface = {}

        if node.name.startswith('S'):
            interface['Name'] = intfName
            interface['VLAN ID'] = 1
            interface['VLAN TYPE'] = 'access'
            # send controller a message about new interface
            node.start(self.controllers)

        elif node.name.startswith('H'):
            interface['Name'] = intfName
            interface['Mask'] = '255.0.0.0'
            interface['IP'] = '10.0.0.'+node.name[1:]
            node.setIP(interface['IP'], 8)
            interface['MAC'] = str(node.MAC())

        n = self.findConfigEntry(node, data)

        if 'interfaces' in n.keys():
            n['interfaces'].append(interface)
        else:
            n['interfaces'] = []
            n['interfaces'].append(interface)

        f = open('config.json', 'w')
        json.dump(data, f)
        f.close()

    def delLink(self, firstId, secondId):
        # Get node objects
        node1 = self.nameToNode[firstId]
        node2 = self.nameToNode[secondId]
        link = self.getLinkBetweenNodes(node1, node2)[0]
        link.intf1.delete()
        link.intf2.delete()
        link.delete()
        self.links.remove(link)

        # Remove interface entry from config file
        self.deleteInterface(node1, firstId+'-'+secondId)
        self.deleteInterface(node2, secondId+'-'+firstId)

        # Read config file
        f = open('config.json', 'r')
        data = json.load(f)
        f.close()

        # Remove link from config
        try:
            data['Links'].remove([firstId, secondId])
        except(KeyError):
            pass

        # Write config file
        f = open('config.json', 'w')
        json.dump(data, f)
        f.close()
        return 'success'
    
    # Get params of a node with specified id
    def getParams(self, id):
 
        # Read config file
        f = open('config.json', 'r')
        data = json.load(f)
        f.close()

        # Find the right node and return its params
        config = self.findConfigEntry(self.nameToNode[id], data)

        return json.dumps(config)

    # Change actual node configuration
    def applyParams(self, nodeId, config):
        result = self.nameToNode[nodeId].setParams(config)
        try:
            self.nameToNode['c0'].configChanged()
        except:
            pass

        return result
    
    # Change node params in configuration file
    def setParams(self, nodeId, config):
        # read config file
        f = open('config.json', 'r')
        data = json.load(f)
        f.close()
        nodeType = self.nodeType(self.nameToNode[nodeId])

        # write new config to file
        f = open('config.json', 'w')
        for index, node in enumerate(data[nodeType], start=0):
            if node['ID'] == nodeId:
                data[nodeType][index] = config
                json.dump(data, f)
                f.close()
                break

        result = self.applyParams(nodeId, config)

        return result

    # Start ping command on a firstId node  
    # with IP from a secondId node
    def ping(self, firstId, secondId):
        return self.nameToNode[firstId].ping(self.nameToNode[secondId].IP())
