# -*- coding: utf-8 -*-

from PyQt4.QtCore import (Qt, QAbstractTableModel, QModelIndex, QVariant,
						QTextStream, QString, QSize, SIGNAL)
from PyQt4.QtGui import QColor, QFont, QStyle, QApplication, QTextDocument, QItemDelegate, QLabel
from constants import *
from packet import Packet
from nodes import NodesModel, Node
import time

#columns:
ACTIVITY, SEQ, PAYLOAD, SRC_ADDR, DST_ADDR = range(5)

class PacketsModel(QAbstractTableModel):
	"""
	This class represents and manages current processed data.
	The data is held in memory as a list.
	"""
	def __init__(self):
		super(PacketsModel, self).__init__()
		self.packets = []
		self.nodes = NodesModel()
		self.changed_ = False
		#self.connect(self.nodes, SIGNAL("changed"), self.changed)
		
	def data(self, index, role=Qt.DisplayRole):
		"""
		This function is used by Qt to obtain data needed by the view.
		It is mandatory for the model to work.
		"""
		if not index.isValid() or not (0 <= index.row() < len(self.packets)):
			return QVariant()
			
		packet = self.packets[index.row()]
		column = index.column()
			
		if role == Qt.DisplayRole:
			if packet.isInvalid:
				if column == ACTIVITY:
					return QVariant('Invalid')
				return QVariant()
			
			if column == ACTIVITY:
				if packet.frameType == TYPE_CMD:
					return QVariant(packet.commandType)
				return QVariant(packet.frameType)
				
			elif column == SEQ:
				return QVariant(packet.seqNumber)
				
			elif column == PAYLOAD:
				if packet.frameType == TYPE_DATA:
					if hasattr(packet, 'payload'):
						return QVariant(packet.payload)
					return QVariant()
					
				elif packet.frameType == TYPE_CMD:
					if hasattr(packet, 'commandPayload'):
						#return QVariant('%s\n(%s)' % (packet.commandType, packet.commandPayload))
						return QVariant(packet.commandPayload)	
					#return QVariant(packet.commandType)
					
				elif packet.frameType == TYPE_BCN:
					return QVariant(packet.bcnPayload)
				return QVariant()
				
			elif column == SRC_ADDR:
				if packet.srcAddrMode in (MODE_16, MODE_64):
					addr = packet.srcAddr if hasattr(packet, 'srcAddr') else '<none>'
					pan = packet.dstPANID if packet.intraPAN == 'Yes' else packet.srcPANID
					# TODO:  internalization will brake this^^^^^^^^^^!!! fix this!
					return QVariant('%s <span style="color:#777;font-size:8pt;">(PAN: %s)</span>' 
								% (self.nodes.getName(addr, pan), pan))
				return QVariant()
			
			elif column == DST_ADDR:
				if packet.dstAddrMode in (MODE_16, MODE_64):
					addr = packet.dstAddr if hasattr(packet, 'dstAddr') else '<none>'
					pan =  packet.dstPANID
					return QVariant('%s <span style="color:#777;font-size:8pt;">(PAN: %s)</span>' 
								% (self.nodes.getName(addr, pan), pan))
				return QVariant()
			
		elif role == Qt.ToolTipRole:
			if packet.isInvalid:
				return QVariant('Recieved packet was invalid, or CRC failded')
			
			if column == ACTIVITY:
				if packet.frameType == TYPE_CMD:
					return QVariant('%s command' % packet.commandType)
				return QVariant('%s frame' % packet.frameType)
				
			elif column == SEQ:
				return QVariant('Sequence number: %s' % packet.seqNumber)
				
			elif column == SRC_ADDR:
				if packet.srcAddrMode in (MODE_16, MODE_64):
					addr = packet.srcAddr if hasattr(packet, 'srcAddr') else '<none>'
					pan = packet.dstPANID if packet.intraPAN == 'Yes' else packet.srcPANID
					# TODO:  internalization will brake this^^^^^^^^^^!!! fix this!
					name = self.nodes.getName(addr, pan)
					if name == addr:
						return QVariant('Node %s in PAN: %s)' % (addr, pan))
					else:
						return QVariant('Node <b>%s</b>, address %s in PAN %s' % (name, addr, pan))
				return QVariant('Address is not available')
			
			elif column == DST_ADDR:
				if packet.dstAddrMode in (MODE_16, MODE_64):
					addr = packet.dstAddr if hasattr(packet, 'dstAddr') else '<none>'
					pan =  packet.dstPANID
					name = self.nodes.getName(addr, pan)
					if name == addr:
						return QVariant('Node %s in PAN: %s)' % (addr, pan))
					else:
						return QVariant('Node <b>%s</b>, address %s in PAN %s' % (name, addr, pan))
				return QVariant('Address is not available')
			
		elif role == Qt.BackgroundColorRole:
			if packet.isInvalid:
				return QVariant(QColor(230, 180, 180))
			if packet.frameType == TYPE_BCN:
				return QVariant(QColor(220, 170, 220))
			elif packet.frameType == TYPE_ACK:
				return QVariant(QColor(215, 235, 195))
			elif packet.frameType == TYPE_DATA:
				return QVariant(QColor(255, 255, 255))
			elif packet.frameType == TYPE_CMD:
				return QVariant(QColor(200, 205, 235))
			
		elif role == Qt.TextAlignmentRole:
			return QVariant(int(Qt.AlignCenter|Qt.AlignVCenter))
		
		return QVariant()
	
	def headerData(self, section, orientation, role=Qt.DisplayRole):
		"""
		This function is used by Qt to obtain columns' headers.
		"""
		if role == Qt.TextAlignmentRole:
			if orientation == Qt.Horizontal:
				return QVariant(int(Qt.AlignCenter|Qt.AlignVCenter))
			return QVariant(int(Qt.AlignCenter|Qt.AlignVCenter))
		if role == Qt.ToolTipRole:
			if section == ACTIVITY:
				return QVariant('Type of frame or command')
			elif section == SEQ:
				return QVariant('Sequence number')
			elif section == PAYLOAD:
				return QVariant('Payload')
			elif section == SRC_ADDR:
				return QVariant("Source address (and source PAN-ID)")
			elif section == DST_ADDR:
				return QVariant("Destination address (and destination PAN-ID)")
		elif role == Qt.DisplayRole:
			if orientation == Qt.Horizontal:
				if section == ACTIVITY:
					return QVariant('Activity')
				elif section == SEQ:
					return QVariant('Seq.')
				elif section == PAYLOAD:
					return QVariant('Payload')
				elif section == SRC_ADDR:
					return QVariant("Source")
				elif section == DST_ADDR:
					return QVariant("Destination")
				return QVariant(int(section + 1)) # if column name unknown, return number
		else:
			return QVariant()
	
	def rowCount(self, index=QModelIndex()):
		"""
		This function is mandatory for the model to work.
		"""
		if not index.isValid():
			return len(self.packets)
		return 0 # <---packets have no children
	
	def columnCount(self, index=QModelIndex()):
		"""
		This function is mandatory for the model to work.
		"""
		return 5
	
	def getPacket(self, index):
		"""
		This function returns packet (Packet) from given index (QModelIndex)
		"""
		return self.packets[index.row()]
	
	def append(self, packet):
		"""
		Adds one packet at end of the packets list
		"""
		self.beginInsertRows(QModelIndex(), len(self.packets), len(self.packets) + 1)
		self.packets.append(packet)
		self.endInsertRows()
		self.changed(True)
		self.nodes.append_from_packet(packet)
	
	def clear(self):
		"""
		Clears the packets list (doesn't clear nodes list)
		"""
		self.beginRemoveRows(QModelIndex(), 0, len(self.packets))
		self.packets = []
		self.endRemoveRows()
	
	def load(self, fh):
		"""
		Load packets from given file handler
		"""
		# first we read all nodes
		for line in filter(lambda l: l.startswith('+NODE:'), fh):
			name = line.rstrip()[line.find('"') + 1:line.rfind('"')]
			line = line.rstrip()[line.rfind('"') + 2:].split(',')
			pan = ''.join(reversed(line[:2])).replace('?', '')
			pan = '0x' + pan.lower() if pan else ''
			address = ''.join(reversed(line[2:4])).replace('?', '')
			address = '0x' + address.lower() if address else ''
			self.nodes.append_unique(Node(pan, address, name))

		# but they are at the end of file so we return to begining now:
		fh.seek(0)
		for line in filter(lambda l: l.startswith('+FRAM:'), fh):
			load, time = (line[19:].split(',')[1:], #load
							line[6:18].split(',')) #time
			load = [int(x, 16) for x in load] #hex->int
			self.append(Packet(load, time))
			
		self.changed(False)
		self.nodes.changed(False)
	
	def save(self, fh):
		"""
		This function writes collected data into a fh file in .154 format
		"""
		#first write head of file
		fh.write('+INFO:IEEE 802.15.4 ZigBeeSniffer Log.\r\n')
		fh.write('+DATE:' + time.ctime() + '\r\n')
		for packet in self.packets:
			load = [len(packet.load)] + packet.load
			load = map(str, map(hex, load))	# int->hex->str
			load = map(lambda x: ('0'+x[2:])[-2:].upper(), load)	# 0xa -> 0A
			load = ','.join(load)						# glue it back
			timee = ','.join(packet.time)
			fh.write('+FRAM:' + timee + ',' + load + '\r\n')
			
		for node in self.nodes.nodes:
			pan = node.panId[2:]     # cut '0x' from begining
			addr = node.address[2:]  # cut '0x' from begining
			line = '+NODE:"%s"' % node.name
			line += ',%s,%s' % (pan[2:], pan[:2]) if pan else ',??,??'  # PAN-ID
			#now split address into pairs (bytes):
			pairs = map(''.join, zip(iter(addr), iter(addr)))
			for pair in reversed(pairs): 
				line += ',%s' % pair
			for i in range(8 - len(pairs)):
				line += ',??'
			line += '\r\n'
			fh.write(line)
		
		self.changed(False)
		
	def changed(self, arg=None):
		if arg is None:
			return self.changed_
		else:
			self.changed_ = arg
			self.emit(SIGNAL("changed"))
			
	
	# ============== methods needed by statistics window ================== 
	def invlaid_count(self):
		return len(filter(lambda packet: packet.isInvalid, self.packets))
		
	def error_rate(self):
		return 100.0 * self.invlaid_count() / self.rowCount()
	
	def coord_count(self):
		coords = filter(lambda packet: hasattr(packet, 'PANCoord'), self.packets)
		return len(filter(lambda packet: packet.PANCoord, coords))
	
	def type_count(self, type, cmd=None):
		if not cmd:
			packets = filter(lambda packet: hasattr(packet, 'frameType'), self.packets)
			return len(filter(lambda packet: packet.frameType == type, packets))
		else:
			commands = filter(lambda packet: hasattr(packet, 'frameType'), self.packets)
			commands = filter(lambda packet: packet.frameType == type, commands)
			return len(filter(lambda packet: packet.commandType == cmd, commands))
	
	


class PacketsDelegate(QItemDelegate): 
	"""
	This is delegate allowing html in list
	"""
	def __init__(self, parent=None):
		super(PacketsDelegate, self).__init__(parent)
		
	def paint(self, painter, option, index):
		if index.column() in (SRC_ADDR, DST_ADDR):
			text = index.model().data(index).toString()
			palette = QApplication.palette()
			document = QTextDocument()
			document.setDefaultFont(option.font)
			if option.state & QStyle.State_Selected:
				document.setHtml("<font color=%s>%s</font>" % 
								(palette.highlightedText().color().name(), text))
				color = palette.highlight().color()
			else:
				document.setHtml(text)
				color = QColor(index.model().data(index, Qt.BackgroundColorRole))
			#document.setPageSize(option.rect.size())
			painter.save()
			painter.fillRect(option.rect, color)
			painter.translate(option.rect.x(), option.rect.y())
			document.drawContents(painter)
			painter.restore()
		else:
			QItemDelegate.paint(self, painter, option, index)
		
	def sizeHint(self, option, index):
		fm = option.fontMetrics
		if index.column() in (SRC_ADDR, DST_ADDR):
			text = index.model().data(index).toString()
			document = QTextDocument()
			document.setDefaultFont(option.font)
			document.setHtml(text)
			#document.setPageSize(option.rect.size())
			return QSize(document.idealWidth() + 5, 1.3 * fm.height())
		return QItemDelegate.sizeHint(self, option, index)
	
	