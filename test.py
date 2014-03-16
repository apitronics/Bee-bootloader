from Xbee import *

Coordinator = Xbee('/dev/ttyUSB0')
Router = Xbee('/dev/ttyUSB1')


#print Coordinator.requestAT("SH")

#for msg in Coordinator.requestAT("SL"):
#	print msg
#	if msg[0:8]==[126, 0, 9, 136, 1, 83, 72, 0]:
#		print "SH: " + str(msg[-5:-1])
#
#for msg in Router.requestAT("SL"):
#	print msg
#        if msg[0:8]==[126, 0, 9, 136, 1, 83, 72, 0]:
#                print "SH: " + str(msg[-5:-1])

print "Coordinator send test"
originalMsg = Coordinator.test(Router.address)

print "Data  : " + str(originalMsg.data)
print "Origin: " + str(originalMsg.origin)
print "Dest  : " + str(originalMsg.destination)


print "Router listening"
for msg in Router.listenForData():
	print "Data  : " + str(msg.data)
	print "Origin: " + str(msg.origin)
	print "Dest  : " + str(msg.destination)

