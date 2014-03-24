from Xbee import *

Coordinator = Xbee('/dev/ttyUSB0')


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
originalMsg = Coordinator.broadcast([0x1,0x2,3,4,5,6,7,8])


print "Data  : " + str(originalMsg.data)
print "Origin: " + str(originalMsg.origin)
print "Dest  : " + str(originalMsg.destination)

