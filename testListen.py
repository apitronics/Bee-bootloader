from Xbee import *

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
while True:
	for msg in Router.listenForData():
		if msg is not None:
			print "Data  : " + str(msg.data)
			print "Origin: " + str(msg.origin)
			print "Dest  : " + str(msg.destination)

