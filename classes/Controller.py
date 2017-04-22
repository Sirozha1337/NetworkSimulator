from mininet.node import Controller as OFController
import os
import signal

class Controller( OFController ):
    def __init__( self, name,
                  command='python ./pox/pox.py',
                  cargs=( 'openflow.of_01 --port=%s '
                          'l2_learning_vlan_support' ),
                  **kwargs ):
        OFController.__init__( self, name, 
                             command=command, port=6633,
                             cargs=cargs, **kwargs )

    def configChanged(self):
        os.kill(self.pid, signal.SIGUSR1)

controllers={ 'pox': Controller }

