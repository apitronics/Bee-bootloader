#!/usr/bin/env python

#Sometimes sudo apt-get install python-serial isn't recent enough and doens't include list_ports
#then you need to download: https://pypi.python.org/packages/source/p/pyserial/pyserial-2.7.tar.gz#md5=794506184df83ef2290de0d18803dd11
#and run: "python setup.py install" from that directory

#This library requires that modules be configured in API mode w/o escape characters!

import logging
from serial.tools.list_ports import *

print "Ports available: "

ports = []
j=0
for i in comports():
		if not i[0].startswith('/dev/ttyS'):
			ports+=[str(i[0])]
			print "   Xbee.ports[" +str(j)+ "]: " + str(i[0])
			j+=1

import serial
import io
import array
import binascii
import os
import time
import struct 
import random

class Message:
	def __init__(self, origin, data, destination, maxPayload=256):
		self.origin=origin
		self.data=data
		self.maxPayload=maxPayload
		self.destination=destination
		self.packets=self._pack(data)
	
	@classmethod
	def unpack(cls,rawData):
		origin = rawData[3:15]
		data = rawData[16:-1]
		print data
		return cls(origin,data,[0])

	def _pack(self, data):
		packets = []
		for i in range(0,len(data)/(self.maxPayload+3)+1): #break data into packets appropriate for network
			packets +=[self._createPacket(data[i*self.maxPayload:min(len(data),(i+1)*self.maxPayload)])]
		return packets

	def _createPacket(self, data):
		packet=[0x7E, 0x00, 0x00, 0x10, 0x01]	#initialize hexAPI with standard beginning
		#Start [Delimiter, MSB (length), LSB (length), Frame Type (ie: transmit), Frame ID (ie: want ACK)]

		packet+=self.destination	#64 bit address
		packet+=[0xFF, 0xFE]   	#16 bit address
		packet+=[0x00, 0x00]   	#radius and options
		
		for i in data:
                 	       packet+=[i]

		length = len(packet)-3
		packet[1]=(length&0xFF00)>>8        
        	packet[2]= length&0x00FF                      
        	packet+= [0xFF-sum(packet[3::])&255]	
		return packet		

class Xbee:
	def __init__(self, port, baud=9600, maximumPayloadSize=256):
		self.port = port
		self.baud = baud
		self.ser = serial.Serial(self.port, self.baud, timeout=1)
		self.ser.flush()
		logging.info("Opened Serial to Xbee on " + self.port)
		self.address=0
		self.maxPayload=maximumPayloadSize

	def test(self, length=12):
		data=[]

		for i in range(0,length):
			data+=[random.randint(0,255)]
		
		msg = self.broadcast(data)
		self.send(msg)

	def broadcast(self, data):
        	return Message(self.address, data, [0,0,0,0,0,0,0xFF,0xFF], self.maxPayload)

	def send(self, Message):	
		for packet in Message.packets:
			print packet
			data = ''			
			for j in packet:
				data+=struct.pack('B',j)
			while not self.ACK():
				self.ser.write(data)
	
	def ACK(self):
		ACK = [126, 0, 7, 139, 1]
		#time.sleep(0.1)
		response = self.listen()
		#print "RESPONSES: "
		#for i in response:
		#	print i
		#ser.write(array.array('B',hexAPI).tostring())
		for i,j in enumerate(response):
			if j[0:5]==ACK:
		#		print "good"
				return True
				#return response[i+1::]
		return False

	def listen(self):
		received=[]
		#limit=3
		#tries=0
		raw='begin'

		while raw!='':
			raw = self.ser.readline()
			if raw!='':
				received+=raw
			#tries+=1
			#if tries>limit:
			#        break

		dec = []
		cur = []
		for i in received:
			if i!=['']:
				cur += [binascii.b2a_qp(i,False,False,False)]
		for i in cur:
			if cmp(i[0],'='):
				dec+=[ord(i)]
			else:
				convert = 0
				for j in range(1,3):
					
					if (ord(i[j])>64):
						convert += (ord(i[j])-55)
					else:
						convert += (ord(i[j])-48)
					if j==1:
						convert=convert*16
						
				dec+=[convert]
		msgs=[]
	 
		for i,j in enumerate(dec):
			try:
				if j==126: #if its beginning of msg
					length = dec[i+1]*256 + dec[i+2] #check how long the msg is
					if i+length+3<len(dec):
						msgs += [dec[i:i+length+4] ] #add element to msgs list
						#print str(length) + ": "+ str(dec[i:i+length+1])
			except:
				print "excepted listen()"
		
		#print str(len(msgs)) + " possible messages"
		#verify checksum
		for i,j in enumerate(reversed(msgs)): #traverse in reverse so that deleting doesn't shift indices 
			#print "Expected checksum: " + str(j[-1])
			#print "Actual checksum  : " + str(0xFF-sum(j[3:-1])&0xFF)
			if j[-1]!=(0xFF-sum(j[3:-1])&255):
				del msgs[i]
				print "Received corrupted message"		

		for i in msgs:
			obj = Message.unpack(i)
			print "Data  : " + str(obj.data)
			print "Origin: " + str(obj.origin)
			
			
		#print str(len(msgs)) + " remaining messages"
		
		return msgs


	def requestAT(self,string):
        	hexAPI=[0x7E, 0x00, 0x04, 0x08, 0x01]
        	self.ser.write(formatAPI(hexAPI, string))
        	return self.listen()

	def setAT(self, string, value):
        	hexAPI=[0x7E, 0x00, 0x04, 0x08, 0x01]
        	self.ser.write(formatAPI(hexAPI, string,value))
		return self.listen()

	def requestRemoteAT(self, string, address):
		hexAPI=[0x7E, 0x00, 0x00, 0x17, 0x01]
		#hexAPI+=address
		hexAPI+=[0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0xFF, 0xFF]
		hexAPI+=[0xF0]
		hexAPI+=[0xFF, 0xFE]   #16 bit address
		hexAPI+=[0]
		for i in string:
			hexAPI+=[ord(i)]
		print "Command: " + str(hexAPI)
		tmp = formatAPI(hexAPI)
		self.ser.write(tmp)
		self.listen()

	def ATCommand(self, string):
		hexAPI=[0x7E, 0x00, 0x00, 0x08, 0x01]
		
		self.send(formatAPI(hexAPI,string))
		return self.listen()


	def formatAPI(self, hexAPI,string=None,value=None):
		if string is not None:
			for i in string:
				hexAPI+=[ord(i)]

		if value is not None:
			hexAPI+=[value]

		hexAPI[2]=len(hexAPI)-3                      
		hexAPI+= [0xFF-sum(hexAPI[3::])&255]
		
		print hexAPI
		return array.array('B',hexAPI).tostring()


	

	def listen2(self):
		received=[]
		limit=3
		tries=0
		while True:
		        received += self.ser.readline()
		        tries+=1
		        if tries>limit:
		                break
		dec = []
		cur = []
		for i in received:
		        cur += [binascii.b2a_qp(i,False,False,False)]
		for i in cur:
		        if cmp(i[0],'='):
		                dec+=[ord(i)]
		        else:
		                convert = 0
		                for j in range(1,3):
		                        
		                        if (ord(i[j])>64):
		                                convert += (ord(i[j])-55)
		                        else:
		                                convert += (ord(i[j])-48)
		                        if j==1:
		                                convert=convert*16
		                                
		                dec+=[convert]
		msgs=[]
		
		for i,j in enumerate(dec):
			try:
		        	if j==126:      #if its beginning of msg
		           		length = dec[i+1]*16**2 + dec[i+2] #check how long the msg is
					msgs += [dec[i:3+(i+length+1)] ] #add element to msgs list
			except:
				print "excepted listen()"
		payloads=[]
		#check the checksum
		for i in msgs:
		        if i[-1]!=(0xFF-sum(i[3:-1])&255):	
		                print "Received corrupted message:" 
				#print i
		                msgs.remove(i)
		return msgs
	

	def listenForPayloads(self):
		msgs = self.listen()
		payloads=[]	
		#for i in msgs:
		if i[3]==144:
			payloads+= [{'origin': i[4:12], 'payload': i[15:len(i)-1]}]
		return payloads

	def mapNetwork(self):
		nodes = []
		data = requestAT("ND")
		for i in data:
			#data is supposed to be: MY, SH, SL, DB, DB, NI
			try:
				if i[2]==25: #this means it is an ND frame
					print "node found"
					nodes+= [[i[10], i[11], i[12], i[13],i[14], i[15], i[16], i[17]]]
			except:
				print "was not ND response"
		return nodes
