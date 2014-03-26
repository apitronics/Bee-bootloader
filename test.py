import thread
from Xbee import *

# manually input address to make testing faster
Coordinator = Xbee('/dev/ttyUSB6', maximumPacketStream=8)
Router = Xbee('/dev/ttyUSB7', maximumPacketStream=8)

# otherwise let the library figure it out
#Coordinator = Xbee('/dev/ttyUSB3')
#Router = Xbee('/dev/ttyUSB4')
#print Router.address()

Coordinator.test(Router.address(), 20000)

while True:
	pass
