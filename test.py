from Xbee import *

Coordinator = Xbee('/dev/ttyUSB3')
Router = Xbee('/dev/ttyUSB4')

print "Coordinator send test"
Coordinator.test()

from time import *
print "Router listening"
#for msg in Router.listen2():
#	print msg

try:
	for i in Router.listen():
		print i
except:
	print "no messages"
