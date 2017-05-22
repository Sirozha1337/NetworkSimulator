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
from Router import Router
from time import sleep

class Topology( Mininet ):
    def __init__( self, user_id, topo=None):
        Mininet.__init__(self, topo=None)
        self.user_id = hex(user_id)[2:].zfill(4)
        self.configFile = 'config' + self.user_id + '.json'
        print(self.user_id)
        try:
            f = open(self.configFile, 'r')
            config = json.load(f)
            f.close() 
            types = ['Switches', 'Routers', 'Hosts']
            for nodeType in types:
                if nodeType in config.keys():
                    for node in config[nodeType]:
                        print('Adding ' + nodeType)
                        self.addNode( nodeType, 0, 0, node['ID'] )

            if 'Links' in config.keys():
                for link in config['Links']:
                    print('Adding links')
                    self.addLink( link[0], link[1] )

        except:
            f = open(self.configFile, 'w+')
            f.write('{ }')
            f.close()
            pass   

       
    def start(self): 
        Mininet.start(self)
        f = open(self.configFile, 'r')
        config = json.load(f)
        f.close()
        types = ['Switches', 'Routers', 'Hosts']
        for nodeType in types:
            if nodeType in config.keys():
                for conf in config[nodeType]:
                    print('Setting ' + nodeType + ' parameters')
                    self.nameToNode[conf['ID']].applyParams(conf)

    # Generates ID for a new node of passed type    
    def generateId(self, nodeType):
        newid = 1
        newtype = nodeType[0].upper()
        for node in self.nameToNode:
                if node.startswith(newtype):
                    if newid <= int(node[5:]):
                        newid = int(node[5:]) + 1
        return newtype + self.user_id + str(newid)

    # Adds node of passed type to the topology
    # Supported types - Switches, Hosts, Routers
    def addNode(self, nodeType, x, y, newid=None):
        if newid is None:
            newid = self.generateId(nodeType)
            config = { }        
            config['ID'] = newid
            config['Name'] = newid[0] + newid[5:]
            if nodeType == 'Switches':
                config['State'] = False
                config['DPID'] = int(newid[5:])
            elif nodeType == 'Routers':
                config['Routing'] = []
                config['interfaces'] = []
            config['x'] = float(x)
            config['y'] = float(y)

            f = open(self.configFile, 'r')
            data = json.load(f)
            f.close()

            if nodeType in data.keys():
                data[nodeType].append(config)
            else:
                data[nodeType] = []
                data[nodeType].append(config)

            f = open(self.configFile, 'w')
            json.dump(data, f)
            f.close()

        if nodeType == 'Switches':
            self.addSwitch( newid, cls=Switch )

        elif nodeType == 'Hosts':
            self.addHost( newid, cls=Host )

        elif nodeType == 'Routers':
            self.addHost( newid, cls=Router )

        return newid

    # Removes node with passed id from topology
    def delNode(self, id):
        node = self.nameToNode[id]

        if node.nodeType == "Switches":
            nodes = ( self.switches )
        elif node.nodeType == "Routers" or node.nodeType == "Hosts":
            nodes = ( self.hosts )

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
        f = open(self.configFile, 'r')
        data = json.load(f)
        f.close()
        
        for nodeEntry in data[node.nodeType]:
            if nodeEntry['ID'] == id:
                data[node.nodeType].remove(nodeEntry)
        
        f = open(self.configFile, 'w')
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

        return 'success'   
    
    def setLink(self, firstId, secondId):
        result = self.addLink(firstId, secondId)
        if result == 'success':
            # add interfaces to config
            self.addInterface(self.nameToNode[firstId], firstId+'-'+secondId)
            self.addInterface(self.nameToNode[secondId], secondId+'-'+firstId)
            # Read config file
            f = open(self.configFile, 'r')
            data = json.load(f)
            f.close()
       
            # Add link to config
            if 'Links' in data.keys():
                data['Links'].append([firstId, secondId])
            else:
                data['Links'] = []
                data['Links'].append([firstId, secondId])

            # Write config file
            f = open(self.configFile, 'w')
            json.dump(data, f)
            f.close()

            if self.nameToNode[firstId].nodeType == "Switches":
                self.nameToNode[firstId].applyParams(self.findConfigEntry(self.nameToNode[firstId], data))
            if self.nameToNode[secondId].nodeType == "Switches":
                self.nameToNode[secondId].applyParams(self.findConfigEntry(self.nameToNode[secondId], data))

        return result

    def getLinkBetweenNodes(self, node1, node2):
        return [ link for link in self.links
                if (node1, node2) in (
                (link.intf1.node, link.intf2.node),
                (link.intf2.node, link.intf1.node) 
                ) ] 

    # Delete interface entry from configuration file
    def deleteInterface(self, node, intfName):
        f = open(self.configFile, 'r')
        data = json.load(f)
        f.close()

        try:
            port = node.ports.get( node.nameToIntf[ intfName ] )
            if port is not None:
                del node.intfs[ port ]
                del node.ports[ node.nameToIntf[ intfName ] ]
                del node.nameToIntf[ intfName ]
        except:
            pass

        node.cmd('ip link delete ' + intfName)
        if node.nodeType == "Switches":
            node.vsctl('del-port', intfName)

        n = self.findConfigEntry(node, data)

        n['interfaces'] = [i for i in n['interfaces'] if i.get('Name') != intfName]

        f = open(self.configFile, 'w')
        json.dump(data, f)
        f.close()

    # returns config entry in data which represents the specified node
    def findConfigEntry(self, node, data):
        n = [ n for n in data[node.nodeType] if n['ID'] == node.name ][0]
        return n

    # Add interface entry in configuration file
    def addInterface(self, node, intfName):
        f = open(self.configFile, 'r')
        data = json.load(f)
        f.close()
        interface = {}

        if node.nodeType == "Switches":
            interface['Name'] = intfName
            interface['VLAN ID'] = 1
            interface['VLAN TYPE'] = 'access'

        elif node.nodeType == "Hosts" or node.nodeType == "Routers":
            interface['Name'] = intfName
            interface['Mask'] = '255.0.0.0'
            if node.nodeType == "Hosts":
                interface['IP'] = '10.0.0.'+node.name[5:]
                interface['Gateway'] = interface['IP']
                interface['MAC'] = str(node.MAC())
            else:
                interface['IP'] = '10.0.1.'+str(len(node.intfs))
                interface['MAC'] = str(node.intfList()[ node.intfNames().index(interface['Name']) ].MAC())

            node.setIP(interface['IP'], 8)

        n = self.findConfigEntry(node, data)

        if 'interfaces' in n.keys():
            n['interfaces'].append(interface)
        else:
            n['interfaces'] = []
            n['interfaces'].append(interface)

        f = open(self.configFile, 'w')
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
        f = open(self.configFile, 'r')
        data = json.load(f)
        f.close()

        # Remove link from config
        try:
            data['Links'].remove([firstId, secondId])
        except(KeyError):
            pass

        # Write config file
        f = open(self.configFile, 'w')
        json.dump(data, f)
        f.close()
        return 'success'
    
    # Get params of a node with specified id
    def getParams(self, id):
 
        # Read config file
        f = open(self.configFile, 'r')
        data = json.load(f)
        f.close()

        # Find the right node and return its params
        config = self.findConfigEntry(self.nameToNode[id], data)

        return json.dumps(config)

    # Change actual node configuration
    def applyParams(self, nodeId, config):
        result = self.nameToNode[nodeId].applyParams(config)
        return result
        
    # Change node params in configuration file
    def setParams(self, nodeId, config):
        result = self.applyParams(nodeId, config)

        # read config file
        f = open(self.configFile, 'r')
        data = json.load(f)
        f.close()
        n = self.findConfigEntry(self.nameToNode[nodeId], data)

        if result == 'success':
            for key in n.keys():
                n[key] = config[key]
            
            # write new config to file
            f = open(self.configFile, 'w')
            json.dump(data, f)
            f.close()
        else:
            self.applyParams(nodeId, n)

        return result

    # Start ping command on a firstId node  
    # with IP from a secondId node
    def ping(self, firstId, secondId):
        return self.nameToNode[firstId].ping(self.nameToNode[secondId].IP())
