import thread
from Xbee import *

# manually input address to make testing faster
Coordinator = Xbee('/dev/ttyUSB4', maximumPacketStream=8)
#Router = Xbee('/dev/ttyUSB9', maximumPacketStream=8)

import time

#print Router.address()

address = [0, 19, 162, 0, 64, 174, 240, 170]

while True:
	Coordinator.remoteAT(address, "D4",4)
	time.sleep(0.2)
	Coordinator.remoteAT(address, "D4",3)
	time.sleep(10)
	#Router.setAT("D0",5)
	#time.sleep(0.5)
	#Router.setAT("D0",4)
	#time.sleep(0.5)
	pass
