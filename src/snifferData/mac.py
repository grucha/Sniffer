# -*- coding: utf-8 -*-
"""
This is a module with all ZigBee related stuff: frame analysis, network analysis etc.
"""
from constants import *

class Mac(object):
	"""
	This class represents MAC frame fields.
	given MAC frame (psdu) should be only PSDU (without PHY fields)
	"""
	
	def __init__(self, psdu):
		# Watch out! 'Bits' in strings are numbered from left to right
		# byt in reality and datasheet - from right to left!
		self.isInvalid = False
		if len(psdu) < 5: # invalid MAC frame!
			self.isInvalid = True
			return
		
		offset = 0
		bits = bins(rev(psdu[:2]))
		offset += 2
		
		#=== Frame control fields here
		self.frameControl = bytes_to_hex(psdu[:2])
		
		self.frameType = FRAME_TYPE.get(bits[-3:], 'Reserved')
		self.securityEnabled = yesno(bits[-4])
		self.framePending = yesno(bits[-5])
		self.ackRequest = yesno(bits[-6])
		self.intraPAN = yesno(bits[-7])
		
		self.dstAddrMode = ADDR_MODE[bits[-12:-10]]
		self.srcAddrMode = ADDR_MODE[bits[:-14]]
		
		#=== Sequence number field here
		self.seqNumber = hex(psdu[offset])
		offset += 1
		
		if self.frameType == TYPE_ACK:
			pass
		elif self.frameType in (TYPE_DATA, TYPE_CMD):
			#===addressing fields here (common for Data frames an Command frames)
			if self.dstAddrMode != MODE_NONE:
				self.dstPANID = bytes_to_hex(rev(psdu[offset:offset+2]))
				offset += 2
				BYTES = how_many_bytes(self.dstAddrMode) #BYTES is all-capitals for readability
				self.dstAddr = bytes_to_hex(rev(psdu[offset:offset+BYTES]))
				offset += BYTES
			if self.srcAddrMode != MODE_NONE:
				if self.dstAddrMode != MODE_NONE and self.intraPAN == yesno('0'):
					self.srcPANID = bytes_to_hex(rev(psdu[offset:offset+2]))
					offset += 2
				BYTES = how_many_bytes(self.srcAddrMode)
				self.srcAddr = bytes_to_hex(rev(psdu[offset:offset+BYTES]))
				offset += BYTES
			
			#=== Payload fields here
			if self.frameType == TYPE_DATA:
				if len(psdu[offset:-2]) > 0:
					self.payload = bytes_to_hex(rev(psdu[offset:-2]))
			else: #TYPE_CMD
				self.commandType = COMMAND_TYPE[hex(int(psdu[offset]))]
				offset += 1
				if len(psdu[offset:-2]) > 0:
					self.commandPayload = bytes_to_hex(rev(psdu[offset:-2]))
		
		elif self.frameType == TYPE_BCN:
			self.srcPANID = bytes_to_hex(rev(psdu[offset:offset+2]))
			offset += 2
			BYTES = how_many_bytes(self.srcAddrMode)
			self.srcAddr = bytes_to_hex(rev(psdu[offset:offset+BYTES]))
			offset += BYTES
			
			#=== Superframe specification fields here (2 bytes):
			bits = bins(rev(psdu[offset : offset + 2]))
			self.superFrameSpec = bytes_to_hex(rev(psdu[offset:offset+2]))
			offset += 2
			self.beaconOrder = hex(int(bits[-4:], 2))
			self.superFrameOrder = hex(int(bits[-8:-4], 2))
			self.finalCAPSlot = hex(int(bits[-12:-8], 2))
			self.battLifeExt = yesno(int(bits[-13], 2))
			self.PANCoord = yesno(int(bits[-15], 2))
			self.assocPermit = yesno(int(bits[-16], 2))
			
			#=== GTS specification field
			self.GTS = hex(psdu[offset])
			bits = bins(psdu[offset])
			offset += 1
			self.GTSDescrCount = hex(int(bits[-3:], 2))
			self.GTSPermit = yesno(int(bits[-8], 2))
			
			#=== GTS directions field here
			if int(self.GTSDescrCount, 16) > 0:
				self.GTSDirections = hex(psdu[offset]) 
				offset += 1
			
				#=== GTS list field here (3 bytes)
				gtsDescrCount = int(self.GTSDescrCount, 16) 
				descriptors = []
				for i in xrange(gtsDescrCount):
					descrN = object()
					descrN.GTSDescriptor = bytes_to_hex(rev(psdu[offset:offset+3]))
					bits = bins(rev(psdu[offset : offset+3]))
					offset += 3
					descrN.deviceShortAddr = hex(int(bits[-16:], 2))
					descrN.GTSStartingSlot = hex(int(bits[-20:-16], 2))
					descrN.GTSLength = hex(int(bits[-24:-20], 2))
					descriptors.append(descrN)
			
				self.GTSDescriptors = descriptors #this is a list of objects
			
			#=== Pending adress fields here
			startOfPending = offset #remember the offset of this fields group
			bits = bins(psdu[offset:offset+1])
			offset += 1
			shortAddrList = []
			longAddrList = []
			self.numShortAddrPnd = hex(int(bits[-3:], 2))
			self.numLongAddrPnd = hex(int(bits[-7:-4], 2))
			for i in xrange(int(self.numShortAddrPnd, 16)):
				shortAddrList.append(bytes_to_hex(rev(psdu[offset:offset+2])))
				offset += 2
			for i in xrange(int(self.numLongAddrPnd, 16)):
				longAddrList.append(bytes_to_hex(rev(psdu[offset:offset+8])))
				offset += 8
			self.pndAddrFields = bytes_to_hex(rev(psdu[startOfPending:offset]))
			self.shortAddrPndList = shortAddrList # WARNING: this is a list!
			self.longAddrPndList  = longAddrList # WARNING: this is a list!
			
			#beacon payload field
			if len(psdu[offset:-2]) > 0:
				self.bcnPayload = bytes_to_hex(rev(psdu[offset:-2]))
		
		#=== and finally for all frame types:
		bits = bins(psdu[-2]) # 2's compliment code
		if bits[0] == '1':  # if negative numbers
			self.RSSI = str(-(255 - int(bits[1:], 2) + 1) - 45) + 'dBm'
		else:
			self.RSSI = str(int(bits[1:], 2) - 45) + 'dBm'
		
		bits = bins(psdu[-1])
		self.CRCOk = yesno(bits[0])
		self.LQI = str(int(bits[1:], 2) - 10) + '%'
		

def yesno(arg):
	if not int(arg):
		return 'No'
	return 'Yes'

def how_many_bytes(addrMode):
	"""
	This function returns byte count for given addressing mode.
	"""
	if addrMode == MODE_16:
		return 2
	elif addrMode == MODE_64:
		return 8
	else:
		return 0 	#this case is not necessary

def bytes_to_hex(addr):
	"""
	This function returns a (hexadecimal) string representation 
	of address given in tuple/list
	"""
	result = ''
	if isinstance(addr, str): #one byte
		return '0x' + ('0' + hex(addr)[2:])[-2:]
	else:	#multiple bytes
		for byte in addr:
			result += ('0' + hex(byte)[2:])[-2:]
		return '0x' + result if len(addr) > 0 else ''
	

def bins(bytes, rev = False):
	"""
	This function converts list of integers into one binary string
	(without preceeding '0b')
	"""
	if isinstance(bytes, int): #one byte
		return ('00000000'+bin(bytes)[2:])[-8:]
	else: #multiple bytes
		return ''.join(map(lambda x: ('00000000'+bin(x)[2:])[-8:], bytes))

def rev(a):
	"""
	This function returns reversed <a> list
	"""
	a.reverse()
	return a

#def find_nodes(packets):
#	"""
#	This function returns dictionary of all nodes taking part in sniffed transmission
#	recorded in <packets>
#	Format {'Node address': 'Name'}
#	"""
#	nodes = {}
#	number = 0
#	for packet in packets:
#		#packet = packet['load']
#		
#		node = (MAC(packet).get('Source address', {}).get('val', '0xffff'))
#		if node not in (None, '0xffff') and not nodes.has_key(node):
#			nodes[node] = 'Node %i' % number
#			number += 1
#			
#		node = (MAC(packet).get('Destination address', {}).get('0xffff'))
#		if node not in (None, '0xffff') and not nodes.has_key(node):
#			nodes[node] = 'Node %i' % number
#			number += 1
#		#nodes += 
#	return nodes