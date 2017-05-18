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
    def __init__( self, topo=None ):
        Mininet.__init__(self, topo=None)
        #Mininet.addController(self, name='c0', ip='127.0.0.1', controller=Controller)
        #self.build()
        try:
            f = open('config.json', 'r')
            config = json.load(f)
            f.close()

            if 'Switches' in config.keys():
                for sw in config['Switches']:
                    print('Adding switches')
                    self.addSwitch( sw['ID'], cls=Switch )
            
            if 'Hosts' in config.keys():
                for host in config['Hosts']:
                    print('Adding hosts')
                    self.addHost( host['ID'], cls=Host )

            if 'Routers' in config.keys():
                for router in config['Routers']:
                    print('Adding routers')
                    self.addHost( router['ID'], cls=Router )

            if 'Links' in config.keys():
                for link in config['Links']:
                    print('Adding links')
                    self.addLink( link[0], link[1] )

        except:
            pass    
       
    def start(self): 
        Mininet.start(self)
        f = open('config.json', 'r')
        config = json.load(f)
        f.close()
        if 'Hosts' in config.keys():
            hosts = [ h for h in self.hosts if h.nodeType == 'Hosts' ]
            for host, hconf in zip(hosts, config['Hosts']):
                print('Setting host parameters')
                host.applyParams(hconf)


        if 'Routers' in config.keys():
            routers = [ r for r in self.hosts if r.nodeType == 'Routers' ]
            for router, rconf in zip(routers, config['Routers']):
                print('Setting router parameters')
                router.applyParams(rconf)

        if 'Switches' in config.keys():
            for sw, sconf in zip(self.switches, config['Switches']):
                print('Setting switch parameters')
                sw.applyParams(sconf)

    # Generates ID for a new node of passed type    
    def generateId(self, nodeType):
        newid = 1
        newtype = nodeType[0].upper()
        for node in self.nameToNode:
                if node.startswith(newtype):
                    if newid <= int(node[1:]):
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
            elif nodeType == 'Routers':
                config['Routing'] = []
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
            self.addSwitch( newid, cls=Switch )
            #self.nameToNode[newid].start(self.controllers)

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
        f = open('config.json', 'r')
        data = json.load(f)
        f.close()
        
        for nodeEntry in data[node.nodeType]:
            if nodeEntry['ID'] == id:
                data[node.nodeType].remove(nodeEntry)
        
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
        #if self.nameToNode[firstId].nodeType == "Switches":
        #    self.nameToNode[firstId].start([])
        #if self.nameToNode[secondId].nodeType == "Switches":
        #    self.nameToNode[secondId].start([])
        return 'success'   
    
    def setLink(self, firstId, secondId):
        result = self.addLink(firstId, secondId)
        print(result)
        if result == 'success':
            # add interfaces to config
            self.addInterface(self.nameToNode[firstId], firstId+'-'+secondId)
            self.addInterface(self.nameToNode[secondId], secondId+'-'+firstId)
            print('Link added')
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

            try:
                if self.nameToNode[firstId].nodeType == "Switches":
                    self.nameToNode[firstId].applyParams(self.findConfigEntry(firstId))
                if self.nameToNode[secondId].nodeType == "Switches":
                    self.nameToNode[secondId].applyParams(self.findConfigEntry(secondId))
                #sleep(1)
                #self.nameToNode['c0'].configChanged()
            except:
                pass

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

    # returns config entry in data which represents the specified node
    def findConfigEntry(self, node, data):
        n = [ n for n in data[node.nodeType] if n['ID'] == node.name ][0]
        return n

    # Add interface entry in configuration file
    def addInterface(self, node, intfName):
        f = open('config.json', 'r')
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
            interface['IP'] = '10.0.0.'+node.name[1:]
            node.setIP(interface['IP'], 8)
            interface['MAC'] = str(node.MAC())
            if node.nodeType == "Hosts":
                interface['Gateway'] = interface['IP']

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
        result = self.nameToNode[nodeId].applyParams(config)
        '''try:
            self.nameToNode['c0'].configChanged()
        except:
            pass'''

        return result
    
    # Change node params in configuration file
    def setParams(self, nodeId, config):
        # read config file
        f = open('config.json', 'r')
        data = json.load(f)
        f.close()
        nodeType = self.nameToNode[nodeId].nodeType

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
