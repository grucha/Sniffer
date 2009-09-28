# -*- coding: utf-8 -*-

from PyQt4.QtCore import Qt, QAbstractTableModel, QModelIndex, QVariant
from PyQt4.QtGui import QFont
#columns
FIELD, VALUE = range(2)

class DetailsModel(QAbstractTableModel):
	"""
	This class represents current selected packet details (fields=>values).
	The data is held in memory as a list.
	"""
	def __init__(self):
		super(DetailsModel, self).__init__()
		self.fields = []
		self.packet = None
		
	def data(self, index, role=Qt.DisplayRole):
		"""
		This function is used by Qt to obtain data needed by the view.
		It is mandatory for the model to work.
		"""
		if not index.isValid() or not (0 <= index.row() < len(self.fields)):
			return QVariant()
		
		
		if role == Qt.DisplayRole:
			if hasattr(index.parent, 'isValid'):
				parent = index.parent.row()
			else:
				parent = None
			#create subset of fields:
			fields = filter(lambda x: x[2] == parent, self.fields)
			return QVariant(fields[index.row()][index.column()])
		return QVariant()
	
	def headerData(self, section, orientation, role=Qt.DisplayRole):
		"""
		This function is used by Qt to obtain columns' headers.
		"""
		if role == Qt.TextAlignmentRole:
			if orientation == Qt.Horizontal:
				return QVariant(int(Qt.AlignCenter|Qt.AlignVCenter))
			return QVariant(int(Qt.AlignCenter|Qt.AlignVCenter))
		
		if role != Qt.DisplayRole:
			return QVariant()
		
		if orientation == Qt.Horizontal:
			if section == FIELD:
				return QVariant('Field')
			elif section == VALUE:
				return QVariant('Value')
		return QVariant(int(section + 1)) 
	
	def rowCount(self, index=QModelIndex()):
		"""
		This function is mandatory for the model to work.
		"""
		if index.isValid():
			parent = index.row()
		else:
			parent = None
		
		return len(filter(lambda x: x[2] == parent, self.fields))
	
	def columnCount(self, index=QModelIndex()):
		"""
		This function is mandatory for the model to work.
		"""
		return 2
	
	def clear(self):
		"""
		Clears the fields list
		"""
		self.beginRemoveRows(QModelIndex(), 0, len(self.fields))
		self.fields = []
		self.endRemoveRows()
	
	def setPacket(self, packet):
		"""
		This function decodes packet's fields
		"""
		self.clear()
		self.packet = packet
		
		fields = self.fields
		
		fields.append(['Reception time', '%s:%s:%s.%s' % tuple(packet.time), None])
		
		if self.packet.isInvalid:
			return
		
		fields.append(['Transmission info', 'CRC passed: %s,  LQI: %s,  RSSI: %s' % (packet.CRCOk, packet.LQI, packet.RSSI), None])
		fields.append(['PHY fields', '', None])
		phy = len(fields) - 1
		fields.append(['Frame length', len(packet.load), phy])
		
		fields.append(['MAC fields', '', None])
		mac = len(fields) - 1
		fields.append(['Frame control', packet.frameControl, mac])
		fields.append(['Frame Type', packet.frameType, mac])
		fields.append(['Security enabled', packet.securityEnabled, mac])
		fields.append(['Frame pending', packet.framePending, mac])
		fields.append(['Ack. request', packet.ackRequest, mac])
		fields.append(['Intra-PAN', packet.intraPAN, mac])
		fields.append(['Dest. addressing mode', packet.dstAddrMode, mac])
		fields.append(['Source addressing mode', packet.srcAddrMode, mac])
		fields.append(['Sequence number', packet.seqNumber, mac])
		
		if hasattr(packet, 'dstPANID'):
			fields.append(['Destination PAN-ID', packet.dstPANID, mac])
		
		if hasattr(packet, 'dstAddr'):
			fields.append(['Destination address', packet.dstAddr, mac])
		
		if hasattr(packet, 'srcPANID'):
			fields.append(['Source PAN-ID', packet.srcPANID, mac])
			
		if hasattr(packet, 'srcAddr'):
			fields.append(['Source address', packet.srcAddr, mac])
			
		if hasattr(packet, 'payload'):
			fields.append(['Payload', packet.payload, mac])
		
		if hasattr(packet, 'commandType'):
			fields.append(['Command type', packet.commandType, mac])
		
		if hasattr(packet, 'commandPayload'):
			fields.append(['Command payload', packet.commandPayload, mac])
		
		if hasattr(packet, 'superFrameSpec'):
			fields.append(['Superframe specification', packet.superFrameSpec, mac])
			sfs = len(fields) - 1
			fields.append(['Beacon order', packet.beaconOrder, sfs])
			fields.append(['Superframe order', packet.superFrameOrder, sfs])
			fields.append(['finalCAPSlot', packet.finalCAPSlot, sfs])
			fields.append(['Batt. life extension', packet.battLifeExt, sfs])
			fields.append(['PAN Coordinator', packet.PANCoord, sfs])
			fields.append(['Association permit', packet.assocPermit, sfs])
		
		if hasattr(packet, 'GTS'):
			fields.append(['GTS specification', packet.GTS, mac])
			gts = len(fields) - 1
			fields.append(['GTS descriptor count', packet.GTSDescrCount, gts])
			fields.append(['GTS permit', packet.GTSPermit, gts])
			if int(packet.GTSDescrCount, 16) > 0:
				fields.append(['GTS directions', packet.GTSDirections, gts])
				fields.append(['GTS descriptors list', '', gts])
				dscList = len(fields) - 1
				for i in xrange(int(packet.GTSDescrCount, 16)):
					fields.append(['Descriptor #'+str(i), '', dscList])
					d = len(fields) - 1
					fields.append(['Device short address', packet.GTSDescriptors[i].deviceShortAddr, d])
					fields.append(['GTS starting slot', packet.GTSDescriptors[i].GTSStartingSlot, d])
					fields.append(['GTS length', packet.GTSDescriptors[i].GTSLength, d])
			
			fields.append(['Pending addresses list', '', gts])
			pnd = len(fields) - 1
			if int(packet.numShortAddrPnd, 16) > 0 or int(packet.numShortAddrPnd, 16) > 0:
				for i in xrange(int(self.numShortAddrPnd, 16)):
					fields.append(['Short addr. #%i' % i, packet.shortAddrPndList[i], pnd])

				for i in xrange(int(self.numLongAddrPnd, 16)):
					fields.append(['Long addr. #%i' % i, packet.longAddrPndList[i], pnd])
		
		if hasattr(packet, 'bcnPayload'):
			fields.append(['Beacon payload', packet.bcnPayload, mac])
		
		self.beginInsertRows(QModelIndex(), 0, len(self.fields)+1)
		self.endInsertRows()
		for field in fields:
			print field






# TODO: delete it!
from PyQt4.QtGui import QTreeWidgetItem
def updatePacketDetails(treeWidget, packet):
	"""
	This function fills QTreeWidget with packet detailed information.
	"""
	#first remove all content
	fontBold = QFont()
	fontBold.setBold(True)
	
	treeWidget.clear()
	
	t = QTreeWidgetItem(treeWidget)
	t.setText(0, 'Reception time')
	t.setText(1, '%s:%s:%s.%s' % tuple(packet.time))
	
	if packet.isInvalid:
			return
	
	trInfo =  QTreeWidgetItem(treeWidget)
	trInfo.setText(0, 'Transmission info')
	trInfo.setText(1, 'CRC passed: %s,  LQI: %s,  RSSI: %s' % (packet.CRCOk, packet.LQI, packet.RSSI))
	
	PHY =  QTreeWidgetItem(treeWidget)
	PHY.setText(0, 'PHY fields')
	PHY.setFont(0, fontBold)

	frameLength = QTreeWidgetItem(PHY)
	frameLength.setText(0, 'Frame length')
	frameLength.setText(1, '%i' % len(packet.load))
	
	MAC =  QTreeWidgetItem(treeWidget)
	MAC.setText(0, 'MAC fields')
	MAC.setFont(0, fontBold)
	
	frameControl = QTreeWidgetItem(MAC)
	frameControl.setText(0, 'Frame control')
	frameControl.setText(1, packet.frameControl)
	
	frameType = QTreeWidgetItem(frameControl)
	frameType.setText(0, 'Frame Type')
	frameType.setText(1, packet.frameType)
	
	securityEnabled = QTreeWidgetItem(frameControl)
	securityEnabled.setText(0, 'Security enabled')
	securityEnabled.setText(1, packet.securityEnabled)
	
	framePending = QTreeWidgetItem(frameControl)
	framePending.setText(0, 'Frame pending')
	framePending.setText(1, packet.framePending)
	
	ackRequest = QTreeWidgetItem(frameControl)
	ackRequest.setText(0, 'Ack. request')
	ackRequest.setText(1, packet.ackRequest)
	
	intraPAN = QTreeWidgetItem(frameControl)
	intraPAN.setText(0, 'Intra-PAN')
	intraPAN.setText(1, packet.intraPAN)
	
	dstAddrMode = QTreeWidgetItem(frameControl)
	dstAddrMode.setText(0, 'Dest. addressing mode')
	dstAddrMode.setText(1, packet.dstAddrMode)
	
	srcAddrMode = QTreeWidgetItem(frameControl)
	srcAddrMode.setText(0, 'Source addressing mode')
	srcAddrMode.setText(1, packet.srcAddrMode)
	
	seqNumber = QTreeWidgetItem(MAC)
	seqNumber.setText(0, 'Sequence number')
	seqNumber.setText(1, packet.seqNumber)
	
	if hasattr(packet, 'dstPANID'):
		dstPANID = QTreeWidgetItem(MAC)
		dstPANID.setText(0, 'Destination PAN-ID')
		dstPANID.setText(1, packet.dstPANID)
	
	if hasattr(packet, 'dstAddr'):
		dstAddr = QTreeWidgetItem(MAC)
		dstAddr.setText(0, 'Destination address')
		dstAddr.setText(1, packet.dstAddr)
	
	if hasattr(packet, 'srcPANID'):
		srcPANID = QTreeWidgetItem(MAC)
		srcPANID.setText(0, 'Source PAN-ID')
		srcPANID.setText(1, packet.srcPANID)
		
	if hasattr(packet, 'srcAddr'):
		srcAddr = QTreeWidgetItem(MAC)
		srcAddr.setText(0, 'Source address')
		srcAddr.setText(1, packet.srcAddr)
		
	if hasattr(packet, 'payload'):
		payload = QTreeWidgetItem(MAC)
		payload.setText(0, 'Payload')
		payload.setText(1, packet.payload)
	
	if hasattr(packet, 'commandType'):
		commandType = QTreeWidgetItem(MAC)
		commandType.setText(0, 'Command type')
		commandType.setText(1, packet.commandType)
	
	if hasattr(packet, 'commandPayload'):
		commandPayload = QTreeWidgetItem(MAC)
		commandPayload.setText(0, 'Command payload')
		commandPayload.setText(1, packet.commandPayload)
	
	if hasattr(packet, 'superFrameSpec'):
		superFrameSpec = QTreeWidgetItem(MAC)
		superFrameSpec.setText(0, 'Superframe specification')
		superFrameSpec.setText(1, packet.superFrameSpec)
	
		beaconOrder = QTreeWidgetItem(superFrameSpec)
		beaconOrder.setText(0, 'Beacon order')
		beaconOrder.setText(1, packet.beaconOrder)
	
		superFrameOrder = QTreeWidgetItem(superFrameSpec)
		superFrameOrder.setText(0, 'Superframe order')
		superFrameOrder.setText(1, packet.superFrameOrder)
	
		finalCAPSlot = QTreeWidgetItem(superFrameSpec)
		finalCAPSlot.setText(0, 'finalCAPSlot')
		finalCAPSlot.setText(1, packet.finalCAPSlot)
	
		battLifeExt = QTreeWidgetItem(superFrameSpec)
		battLifeExt.setText(0, 'Batt. life extension')
		battLifeExt.setText(1, packet.battLifeExt)
	
		PANCoord = QTreeWidgetItem(superFrameSpec)
		PANCoord.setText(0, 'PAN Coordinator')
		PANCoord.setText(1, packet.PANCoord)
	
		assocPermit = QTreeWidgetItem(superFrameSpec)
		assocPermit.setText(0, 'Association permit')
		assocPermit.setText(1, packet.assocPermit)
	
	if hasattr(packet, 'GTS'):
		GTS = QTreeWidgetItem(MAC)
		GTS.setText(0, 'GTS specification')
		GTS.setText(1, packet.GTS)
	
		GTSDescrCount = QTreeWidgetItem(GTS)
		GTSDescrCount.setText(0, 'GTS descriptor count')
		GTSDescrCount.setText(1, packet.GTSDescrCount)
		
		GTSPermit = QTreeWidgetItem(GTS)
		GTSPermit.setText(0, 'GTS permit')
		GTSPermit.setText(1, packet.GTSPermit)
		
		if int(packet.GTSDescrCount, 16) > 0:
			GTSDirections = QTreeWidgetItem(GTS)
			GTSDirections.setText(0, 'GTS directions')
			GTSDirections.setText(1, packet.GTSDirections)
		
			GTSDescriptors = QTreeWidgetItem(GTS)
			GTSDescriptors.setText(0, 'GTS descriptors list')
			descriptors = []
			for i in xrange(int(packet.GTSDescrCount, 16)):
				descriptor = [QTreeWidgetItem(GTSDescriptors)] * 3
				descriptor[0].setText(0, 'Device short address')
				descriptor[0].setText(1, packet.GTSDescriptors[i].deviceShortAddr)
				descriptor[1].setText(0, 'GTS starting slot')
				descriptor[1].setText(1, packet.GTSDescriptors[i].GTSStartingSlot)
				descriptor[2].setText(0, 'GTS length')
				descriptor[3].setText(1, packet.GTSDescriptors[i].GTSLength)
				descriptors.append(descriptor)
		
		if int(packet.numShortAddrPnd, 16) > 0 or int(packet.numShortAddrPnd, 16) > 0:
			pendingAddr = QTreeWidgetItem(MAC)
			pendingAddr.setText(0, 'Pending addresses list')
			pndShort = []
			pndLong = []
			for i in xrange(int(packet.numShortAddrPnd, 16)):
				pndShort.append(QTreeWidgetItem(pendingAddr))
				pndShort[i].setText(0, 'Pending short addr. #%i' % i)
				pndShort[i].setText(1, packet.shortAddrPndList[i])
			for i in xrange(int(packet.numLongAddrPnd, 16)):
				pndLong.append(QTreeWidgetItem(pendingAddr))
				pndLong[i].setText(0, 'Pending long addr. #%i' % i)
				pndLong[i].setText(1, packet.longAddrPndList[i])
			
	if hasattr(packet, 'bcnPayload'):
		bcnPayload = QTreeWidgetItem(MAC)
		bcnPayload.setText(0, 'Beacon payload')
		bcnPayload.setText(1, packet.bcnPayload)
	
	
	