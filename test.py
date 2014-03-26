import thread
from Xbee import *

# manually input address to make testing faster
Coordinator = Xbee('/dev/ttyUSB0')
Router = Xbee('/dev/ttyUSB1',[0, 19, 162, 0, 64, 174, 240, 170])

# otherwise let the library figure it out
#Coordinator = Xbee('/dev/ttyUSB3')
#Router = Xbee('/dev/ttyUSB4')
#print Router.address()

Coordinator.test()

while True:
	pass
