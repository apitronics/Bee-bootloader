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

def checksum(msg):
	if msg[-1]!=(0xFF-sum(msg[:-1])&255):
			print "msg failed checksum: "+ str(msg)
                        return False
	return True

class ATRequest:
	def __init__(self, request):
		self.request=request
		self.packet=self._makePacket(request)

	def _makePacket(self, string):
                hexAPI=[0x7E, 0x00, 0x04, 0x08, 0x01]
                cmd = self._stringToHex(string)
                hexAPI+=cmd
                #print "Requesting AT#"+string
                hexAPI[2]=len(hexAPI)-3
                hexAPI+= [0xFF-sum(hexAPI[3::])&255]
		return hexAPI

	def _stringToHex(self, string):
                ret=[]
                for i in string:
                        ret+=[ord(i)]
                return ret


		
class Data:
	def __init__(self, origin, data, frame, destination=[0,0,0,0,0,0,0xFF,0xFF], maxPayload=256):
		self.origin=origin
		self.data=data
		self.maxPayload=maxPayload
		self.destination=destination
		self.frame=frame
		self.packets=self._pack(data)
	
	@classmethod
	def unpack(cls,packets,dest):
		dataGathered={}
		ref={}
		#check that they are all from the same person and have the same data frame
		for index,packet in enumerate(packets):
			if index==0:
				ref={'origin': packet[1:9], 'frame':packet[12]>>4}
			else:
				if ref['origin']!=packet[1:9]:
					print "packet from different person"
				if ref['frame']!=packet[12]>>4:
					print "packet is of different frame"
			#just in case they come out of order
			dataGathered[ (packet[12]&0xF)<<4 | packet[13] ] = packet[14:-1]
		
		data = []
		for i in range(0,len(dataGathered)):
			try:
				data+=dataGathered[i]
			except:
				print "missed a packet #" + str(i)	
		
		
		
		return cls(ref['origin'],data,ref['frame'], dest, )

        @classmethod
	def ATrequest(self, string):
		hexAPI=[0x7E, 0x00, 0x04, 0x08, 0x01]
                cmd = self.stringToHex(string)
                hexAPI+=cmd

                print "Requesting AT#"+string
                hexAPI[2]=len(hexAPI)-3
                hexAPI+= [0xFF-sum(hexAPI[3::])&255]
                
		return clas([0],hexAPI,[0])	

	def _pack(self, data):
		packets = []
		dataPerPacket = self.maxPayload-2

		j=0
		for i in range(0,len(data)/dataPerPacket+1): #break data into packets appropriate for network
			packets +=[self._createPacket(data[i*dataPerPacket:min(len(data),(i+1)*dataPerPacket)], j)]
			j+=1
		print "data broken up into " + str(j) + " packets"
		return packets

	def _createPacket(self, data, index):
		packet=[0x7E, 0x00, 0x00, 0x10, 0x01]	#initialize hexAPI with standard beginning
		#Start [Delimiter, MSB (length), LSB (length), Frame Type (ie: transmit), Frame ID (ie: want ACK)]		
		#print "Index: " +str(index)
		#print self.destination
		packet+=self.destination	#64 bit address
		packet+=[0xFF, 0xFE]   		#16 bit address
		packet+=[0x00, 0x00]   		#radius and options
		packet+=[self.frame & index>>8]	#Apitronics frame (4 bits), upper 4 bits of index
		packet+=[0xFF & index]		#lower 4 bits of index
		for i in data:
                 	       packet+=[i]

		length = len(packet)-3
		packet[1]=(length&0xFF00)>>8        
        	packet[2]= length&0x00FF                      
        	packet+= [0xFF-sum(packet[3::])&255]	
		return packet		

escapeBytes = [0x7E, 0x7D, 0x11, 0x13]

ApitronicsFrame = {'programFlash':0b010, 'settings':0b001, 'dummy':0b000}

class Xbee:
	def __init__(self, port, address=None,  baud=9600, maximumPayloadSize=256, maximumPacketStream=30, escape=True):
		self.escape = escape
		self.port = port
		self.baud = baud
		self.ser = serial.Serial(self.port, self.baud, timeout=1)
		self.ser.flush()
		logging.info("Opened Serial to Xbee on " + self.port)
		if address==None:
			self.address=self.requestAT("SH")+self.requestAT("SL")
		else:
			self.address=address
		self.maxPayload=maximumPayloadSize
		self.maxPacketStream=maximumPacketStream

	def test(self, destination, length=512):
		data=[]

		for i in range(0,length):
			data+=[random.randint(0,255)]
		
		msg = Data(self.address, data, ApitronicsFrame['dummy'], destination)
	
		for i in range(0,len(msg.packets)/self.maxPacketStream+1):	
			for packet in msg.packets[i*self.maxPacketStream:min(len(msg.packets),(i+1)*self.maxPacketStream)]:
				self.send(packet)
			if len(msg.packets)>(i+1)*self.maxPacketStream:
				self.waitForACK()
			  

		#for packet in msg.packets:
		#	self.send(packet)
		return msg

	def waitForACK(self):
		print "WAITING FOR ACK"
		while True:
			
			print "ack?: " + str(self.listen())

	def broadcast(self, data):
		msg = Data(self.address, data, ApitronicsFrame['dummy'], self.maxPayload)
		for packet in msg.packets:
			self.send(packet)
		return msg

	def send(self, rawPacket):	
		#the start delimiter does not get escaped
		packet = rawPacket[:1]
		rawPacket = rawPacket[1:]
		if self.escape:
			#print "dealing with escape"
			for byte in rawPacket:
				if byte in escapeBytes:
					#print "found escape"
					packet+=[0x7D,byte^0x20]
				else:
					packet+=[byte]
		else:
			packet+=rawPacket		
		
		data = ''
		for j in packet:
			data+= struct.pack('B',j)
				
		self.ser.write(data)

	def ACK(self):
		ACK = [126, 0, 7, 139, 1]
		response = self.listen()
		
		for i,j in enumerate(response):
			if j[0:5]==ACK:
				return True
		return False

	def listenForData(self):
		rec = self.listen()
		#print rec
		if rec!=[]:
			#print "UNPACKING"
			return Data.unpack(rec,self.address)
		else:
			return None

	def listen(self):
		received=[]
		raw='begin'

		while raw!='':
			raw = self.ser.readline()
			if raw!='':
				received+=raw
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
		


		if self.escape:
			decNoEscape = []
			for index,byte in enumerate(dec):
				if byte==0x7D:
					decNoEscape += [ dec[index+1]  ^ 0x20]
					del dec[index+1]
				else:
					decNoEscape += [ byte ]

			dec = decNoEscape	
		
		rawMsgs=[]
		for i,j in enumerate(dec):
			if j==126 and : #if its beginning of msg
				length = dec[i+1]*256 + dec[i+2] #parse msg length
				if i+length+3<len(dec):
					potentialMsg = dec[i+3:i+length+4]
					if checksum(potentialMsg):
						rawMsgs+=[potentialMsg]

		return rawMsgs

	def stringToHex(self, string):
		ret=[]
		for i in string:
			ret+=[ord(i)]
		return ret
		
	def requestAT(self,string):
		self.send(ATRequest(string).packet)
		
		cmd=[]
		for i in string:
			cmd+=[ord(i)]         	
		for i in self.listen():
			if i[:2]==[136,1]: 	#valid AT response
				#print i
				#print "actual: " + str(i[2:4]) + ", expected: " + str(cmd)
				if i[2:4]==cmd: #response to our AT
					print i[5:-1]
					return i[5:-1]

			else:
				print "failed checksum: " + str(i)

	def setAT(self,string,value):
        	hexAPI=[0x7E, 0x00, 0x04, 0x08, 0x01]
		hexAPI+=self.stringToHex(string)
        	self.ser.write(self.formatAPI(hexAPI, value))
		return self.listen()

	def requestRemoteAT(self, string, address):
		hexAPI=[0x7E, 0x00, 0x00, 0x17, 0x01]
		#hexAPI+=address
		hexAPI+=[0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0xFF, 0xFF]
		hexAPI+=[0xF0]
		hexAPI+=[0xFF, 0xFE]   #16 bit address
		hexAPI+=[0]
		hexAPI+=self.stringToHex(string)
		print "Command: " + str(hexAPI)
		tmp = self.formatAPI(hexAPI)
		self.ser.write(tmp)
		self.listen()

	def ATCommand(self, string):
		hexAPI=[0x7E, 0x00, 0x00, 0x08, 0x01]
                
		for i in string:
	                hexAPI+=[ord(i)]

		self.send(self.formatAPI(hexAPI,string))
		return self.listen()


	def formatAPI(self, hexAPI, value=None):
		if value is not None:
			hexAPI+=[value]
		hexAPI[2]=len(hexAPI)-3                      
		hexAPI+= [0xFF-sum(hexAPI[3::])&255]
		return hexAPI

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
