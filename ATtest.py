import thread
from Xbee import *

# manually input address to make testing faster
Coordinator = Xbee('/dev/ttyUSB6', maximumPacketStream=8)
Router = Xbee('/dev/ttyUSB7', maximumPacketStream=8)

import time

while True:

	Router.setAT("D0",5)
	time.sleep(0.5)
	Router.setAT("D0",4)
	time.sleep(0.5)
	pass
