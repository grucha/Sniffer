'''
Created on 2009-09-07

@author: sylwek
'''
from PyQt4.QtCore import Qt, QAbstractTableModel, QVariant, QModelIndex, SIGNAL
from PyQt4.QtGui import QFont 
from snifferData.constants import *

class Node(object):
	def __init__(self, panId, address, name=''):
		self.panId = str(panId)
		self.address = str(address)
		self.name = str(address) if not name else str(name)

NAME, PANID, ADDRESS  = range(3)

class NodesModel(QAbstractTableModel):
	'''
	This class represents and holds network nodes data.
	'''

	def __init__(self):
		super(NodesModel, self).__init__()
		self.nodes = [] 
		self.changed_ =  False
	
	def data(self, index, role=Qt.DisplayRole):
		"""
		This function is used by Qt to obtain data needed by the view.
		It is mandatory for the model to work.
		"""
		if not index.isValid() or not (0 <= index.row() < len(self.nodes)):
			return QVariant()
			
		node = self.nodes[index.row()]
		column = index.column()
			
		if role == Qt.DisplayRole:
			if column == PANID:
				return QVariant(node.panId)
				
			elif column == ADDRESS:
				return QVariant(node.address)
				
			elif column == NAME:
				return QVariant(node.name)

		elif role == Qt.FontRole:
			if column in (PANID, ADDRESS):
				font = QFont()
				font.setFamily("DejaVu Sans Mono")
				return font
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
			if section == NAME:
				return QVariant('Name')
			elif section == PANID:
				return QVariant('PAN-ID')
			elif section == ADDRESS:
				return QVariant('Address')
		return QVariant(int(section + 1)) # if column name unknown, return number
	
	def rowCount(self, index=QModelIndex()):
		"""
		This function is mandatory for the model to work.
		"""
		if not index.isValid():
			return len(self.nodes)
		return 0 # <---nodes have no children
	
	def columnCount(self, index=QModelIndex()):
		"""
		This function is mandatory for the model to work.
		"""
		return 3
	
	def flags(self, index):
		"""
		This function is mandatory for model to work with editing data.
		"""
		if not index.isValid() or index.column() != NAME:
			return Qt.ItemIsEnabled
		return Qt.ItemFlags(QAbstractTableModel.flags(self, index) | Qt.ItemIsEditable)
			
	
	def setData(self, index, value, role=Qt.EditRole):
		"""
		Sets the given value to item at given index.
		This function is mandatory for model to work with editing data.
		"""
		print "dupa"
		if index.isValid() and 0 <= index.row() <= len(self.nodes):
			node = self.nodes[index.row()]
			column = index.column()
			if column == NAME:
				node.name = value.toString()
			elif column == ADDRESS:
				node.address = value.toString
			elif column == PANID:
				node.panId = value.toString()
			self.emit(SIGNAL("dataChanged(QModelIndex, QModelIndex)"), index, index)
			self.changed(True)
			return True
		return False 
	
	def getPacket(self, index):
		"""
		This function returns packet (Packet) from given index (QModelIndex).
		"""
		return self.nodes[index.row()]
	
	def append(self, node):
		"""
		Adds a node to nodes list.
		"""
		self.beginInsertRows(QModelIndex(), len(self.nodes), len(self.nodes) + 1)
		self.nodes.append(node)
		self.endInsertRows()
		self.changed(True)
		
	def append_unique(self, node):
		"""
		Appends node if there isn't so in nodes list
		"""
		if len(filter(lambda n: n.panId == node.panId and n.address == node.address, self.nodes)) == 0:
			self.append(node)
	
	def append_from_packet(self, packet):
		"""
		Extract nodes addressess from given packet and append this nodes if they aren't
		alredy in nodes list.
		"""
		for node in self.packet_to_nodes(packet):  # x is an element of self.nodes list
			if node.name == node.address:
				if node.address == node.panId == '0xffff':
					node.name = 'General'
				else:
					node.name = 'Node %d' % self.rowCount(QModelIndex())
			self.append_unique(node)
	
	def packet_to_nodes(self, packet):
		"""
		Extract nodes addressess from addressing information. Return a list (containing none, one or two nodes).
		"""
		nodes = []
		try:
			if not (packet.isInvalid or packet.frameType == TYPE_ACK):
				if packet.dstAddrMode in (MODE_16, MODE_64):
					nodes.append(Node(packet.dstPANID, packet.dstAddr))
				if packet.srcAddrMode in (MODE_16, MODE_64):
					if packet.intraPAN == 'Yes':  # Source PAN-ID not present, TODO: internalization will brake this!!!
						nodes.append(Node(packet.dstPANID, packet.srcAddr))
					else:
						nodes.append(Node(packet.srcPANID, packet.srcAddr))

		except AttributeError, e:
			print(e.message)   # TODO: whats this
			print(dir(packet)) # TODO: remove this...???
		finally:
			return nodes 
	
	def clear(self):
		"""
		Clears the nodes list
		"""
		self.beginRemoveRows(QModelIndex(), 0, len(self.nodes))
		self.nodes = []
		self.endRemoveRows()  # list is cleared only on 'new file' or 'import file',
		self.changed(False)  # so it shouldn't indicate change

	def getName(self, address, panId):
		out = filter(lambda node: node.panId == panId and node.address == address, self.nodes)
		if len(out) > 0:
			return out[0].name
		return address
	
	def changed(self, arg=None):
		if arg is None:
			return self.changed_
		else:
			self.changed_ = arg
			self.emit(SIGNAL("changed"))

