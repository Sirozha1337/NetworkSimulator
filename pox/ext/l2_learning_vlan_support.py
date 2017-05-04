"""
This component is an L2 Learning switch with VLAN access and dot1q support 
"""

from pox.core import core
import pox.openflow.libopenflow_01 as of
from pox.lib.packet.ethernet import ethernet
import signal
import json
import os

log = core.getLogger()

switches = {}

class l2_learning_vlan_support (object):
  """
  A L2Switch object is created for each switch that connects.
  A Connection object for that switch is passed to the __init__ function.
  """
  def __init__ (self, connection):
    # Keep track of the connection to the switch so that we can
    # send it messages!
    self.connection = connection
    
   # signal.signal(signal.SIGUSR1, reloadConfig)  
    # This binds our PacketIn event listener
    connection.addListeners(self)

    # Use this table to keep track of which ethernet address is on
    # which switch port (keys are MACs, values are ports).
    self.mac_to_port = {}

    self.vlan_to_port = {}
    self.vlan_type_to_port = {}
    self.vlan_to_port[65534] = 0 # ignore 
    self.vlan_type_to_port[65534] = 'controller'
	
    log.debug( self.connection.dpid )    

  def resendPacket (self, packet_in, out_ports):
    """
    Instructs the switch to resend a packet that it had sent to us.
    "packet_in" is the ofp_packet_in object the switch had sent to the
    controller due to a table-miss.
    """
    log.debug( "Sending out: %s" % out_ports )

    msg = of.ofp_packet_out()
    msg.data = packet_in
    
    # Add actions for each out port
    for out_port in out_ports:
      # If port is dot1q put on vlan tag
      if self.vlan_type_to_port[out_port] == "dot1q":
        action = of.ofp_action_vlan_vid(vlan_vid = self.vlan_to_port[packet_in.in_port])
      # Else strip vlan tag
      else:
        action = of.ofp_action_strip_vlan()
      msg.actions.append(action)
      
      # Send the packet out of the specified port
      action = of.ofp_action_output(port = out_port)
      msg.actions.append(action)

    # Send message to switch
    self.connection.send(msg)
    log.debug("Packet sent out: %s" % out_ports )
    

  def actLikeSwitch (self, packet, packet_in):
    """
    Implement switch-like behavior.
    """

    # Here's some psuedocode to start you off implementing a learning
    # switch.  You'll need to rewrite it as real Python code.
    log.debug("DPID: %s" % self.connection.dpid)

    # Learn source vlan of the packet
    if packet.type == ethernet.VLAN_TYPE:
      src_vlan = packet.find('vlan').id
    else:
      src_vlan = self.vlan_to_port[packet_in.in_port]

    log.debug("Source VLAN: %s" % src_vlan) 

    # Learn the port for the source MAC
    self.mac_to_port[packet.src] = packet_in.in_port # add or update mac table entry

    # Ports to send out the packet
    out_ports = []

    #if the port associated with the destination MAC of the packet is known
    if packet.dst in self.mac_to_port: 
      log.debug("Mac is in table")

      dst_vlan = self.vlan_to_port[self.mac_to_port[packet.dst]]
      dst_vlan_type = self.vlan_type_to_port[self.mac_to_port[packet.dst]]

      #if the port is in the same vlan as sending port
      if src_vlan == dst_vlan or dst_vlan_type == "dot1q":

        # Send packet out the associated port
        out_ports.append(self.mac_to_port[packet.dst])
        self.resendPacket(packet_in, out_ports)
        
        log.debug("Installing flow. Source port: %s. Destination port: %s.", packet_in.in_port, self.mac_to_port[packet.dst])

        # Install the flow table entry
        msg = of.ofp_flow_mod()

        ## Set fields to match received packet
        msg.match = of.ofp_match(dl_dst = packet.dst)
        
        #< Set other fields of flow_mod (timeouts? buffer_id?) >
        msg.idle_timeout = 10
        msg.hard_timeout = 10
        
        # Add action to add vlan tag or strip it
        if dst_vlan_type == "dot1q":
          action = of.ofp_action_vlan_vid(vlan_vid = src_vlan)
        else:
          action = of.ofp_action_strip_vlan()
        msg.actions.append(action)

        # Add action to resend packet out of the specified port
        msg.actions.append(of.ofp_action_output(port = self.mac_to_port[packet.dst]))
        self.connection.send(msg)
        
    else:
      # Sending to all ports in same vlan as the input port or dot1q port, ignore port connected to controller
      log.debug("Adress is not in table, flooding: ")
      for port in self.connection.ports:
        if port != packet_in.in_port and (self.vlan_to_port[port] == src_vlan or self.vlan_type_to_port[port] == "dot1q"):
           out_ports.append(port)
      log.debug(out_ports)
      if len(out_ports) > 0:
        self.resendPacket(packet_in, out_ports)


  def _handle_PacketIn (self, event):
    """
    Handles packet in messages from the switch.
    """
    
    f = open('controller.log', 'a')
    f.write('handle packet in\n')
    f.close()
    packet = event.parsed # This is the parsed packet data.
    if not packet.parsed:
      log.warning("Ignoring incomplete packet")
      return

    packet_in = event.ofp # The actual ofp_packet_in message.

    self.actLikeSwitch(packet, packet_in)

def launch ():
  """
  Starts the component
  """
  logfile = open('controller.log', 'w+')
  logfile.write('start\n')
  logfile.close()
  def start_switch (event):
  #  some debug lines 
    log.debug( event.connection.ports )
    log.debug("Controlling %s" % (event.connection,))
    print(event.connection.dpid)
    switches[event.connection.dpid] = l2_learning_vlan_support(event.connection)
    logfile = open('controller.log', 'a')
    logfile.write('switch connected\n')
    logfile.write(str(switches.items())+'\n')
    logfile.close()
    os.kill(os.getpid(), signal.SIGUSR1)

  def reloadConfig(signum, frame):
    global switches
    log.debug('reloading config')
    logfile = open('controller.log', 'a')
    logfile.write(str(switches.items())+'\n')
    logfile.write(str(switches.keys())+'\n')
    logfile.write('reloading config\n')
    try:
        f = open('config.json', 'r')
        log.debug('File opened')
        config = json.load(f)
        log.debug('File read')
        logfile.write('File read\n')
    except IOError:
        log.debug('Failed to open file')
        f.close()
        logfile.write('Error')
        return
    log.debug("Connected Switches %s" % switches)
    logfile.write(json.dumps(config) + '\n')
    for sw in config['Switches']:
        i = 1
        if 'interfaces' in sw.keys():
            for interface in sw['interfaces']:
                logfile.write('for intf\n')
                logfile.write(str(sw['DPID']))
                if sw['DPID'] in switches.keys():
                    logfile.write('\nDPID: ' + str(sw['DPID'])+'\n')
                    logfile.write('Set vlan id ' + str(interface['VLAN ID'])+'\n')
                    logfile.write('Set vlan type ' + interface['VLAN TYPE']+'\n')
                    switches[int(sw['DPID'])].vlan_to_port[i] = interface['VLAN ID']
                    switches[int(sw['DPID'])].vlan_type_to_port[i] = interface['VLAN TYPE']
                else:
                    log.debug("Switch didn't connect to controller yet")
                    logfile.write('switch didnt connect yet\n')
                i += 1
        else:
            logfile.write('no intfs\n')
            pass
    log.debug('Config reloaded')
    logfile.write('config reloaded\n')
    logfile.close()

  # Create controller instance
  core.openflow.addListenerByName("ConnectionUp", start_switch)
  # Set signal handler
  signal.signal(signal.SIGUSR1, reloadConfig)

