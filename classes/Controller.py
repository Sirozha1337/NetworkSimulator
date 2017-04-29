from mininet.node import Controller as OFController
import os
import signal
#python ./pox/pox.py
class Controller( OFController ):
    def __init__( self, name,
                  command='./pox/pox.py', 
                  cargs=( 'openflow.of_01 --port=%s '
                          'l2_learning_vlan_support' ),
                  **kwargs ):
        OFController.__init__( self, name, 
                             command=command, port=6633,
                             cargs=cargs, shell=False, **kwargs )
        # Create variable for storing pid of a running controller
        self.realpid = -1

    def configChanged(self):
        # Initialize pid variable
        if self.realpid == -1:
            self.realpid = int(self.cmd("ps aux | grep 'python2.7 -u ./pox/pox.py openflow.of_01 --port=6633 l2_learning_vlan_support' | grep -v grep | awk '{print $2}'"))
        print self.realpid
        print self.cmd("ps aux | grep 'python2.7 -u ./pox/pox.py openflow.of_01 --port=6633 l2_learning_vlan_support'")
        # Send the signal to update config
        os.kill(self.realpid, signal.SIGUSR1)

controllers={ 'pox': Controller }

