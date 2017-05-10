# NetworkSimulator
### What is NetworkSimulator?
NetworkSimulator emulates a complete network of hosts, links, and switches on a single machine and provides access to this network through simple web interface. 
### How does it work?
NetworkSimulator uses mininet for network emulation and pox-controller for switch emulation.
### Dependencies
* Flask
  * sudo pip install flask
* Mininet
  * sudo apt-get install mininet
### Quick start
* Clone repo
  * git clone https://github.com/Sirozha1337/NetworkSimulator.git
* cd to cloned repo
  * cd NetworkSimulator 
* Run 'sudo python Builder.py'
* Open '127.0.0.1:5000' in your browser
* Use Ctrl+C to stop the server
* Run 'sudo mn -c' to clean up after it
### Basic actions
* Adding hosts/switches
  * Click host/switch button on the Tools panel to activate 'add host/switch' mode
  * Click on free space on the Canvas
  * Click host/switch button again to deactivate 'add host/switch' mode
* Adding links
  * Click on one node to activate 'add link' mode
  * Click on another node to add link between them
* Removing hosts/switches
  * Click cross icon near the node you want to remove
* Removing links
  * Double-click the link you want to remove
* Changing node configuration
  * Press gear icon near the node you want to configure
  * Node parameters will appear on the Configuration panel
  * Configure them the way you like and press 'Enter'
* Use ping tool
  * Click 'Ping' button on Tools panel
  * Click on host on which you want to run ping command
  * Click on host which will receive pings
  * Wait until it completes(could take up to 5 seconds)
  * The output of the command will appear in Status Panel
