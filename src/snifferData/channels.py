# -*- coding: utf-8 -*-

from PyQt4.QtCore import Qt, QAbstractTableModel, QModelIndex, QVariant, SIGNAL

#columns:
CHN, FREQ, LQI, BCN = range(4)

class ChannelsModel(QAbstractTableModel):
	"""
	This class represents and manages current processed data.
	The data is held in memory as a list.
	"""
	def __init__(self):
		super(ChannelsModel, self).__init__()
		self.channels = []
		for i in range(16):
			self.append(map(str, [(i+11), (2405+5*i), 0, 0]))
		self.dataChanged = False
		
	def data(self, index, role=Qt.DisplayRole):
		"""
		This function is used by Qt to obtain data needed by the view.
		It is mandatory for the model to work.
		"""
		if not index.isValid() or not (0 <= index.row() < len(self.channels)):
			return QVariant()
			
		channel = self.channels[index.row()]
		column = index.column()
			
		if role == Qt.DisplayRole:
				return QVariant(channel[column])
		
		if role == Qt.TextAlignmentRole:
			return QVariant(int(Qt.AlignCenter|Qt.AlignVCenter))
		return QVariant()
	
	def headerData(self, section, orientation, role=Qt.DisplayRole):
		"""
		This function is used by Qt to obtain columns' headers.
		"""
		if role == Qt.TextAlignmentRole:
			return QVariant(int(Qt.AlignCenter|Qt.AlignVCenter))
		
		if role != Qt.DisplayRole:
			return QVariant()
		if orientation == Qt.Horizontal:
			if section == CHN:
				return QVariant('Chn.')
			elif section == FREQ:
				return QVariant('Freq.')
			elif section == LQI:
				return QVariant('LQI')
			elif section == BCN:
				return QVariant("Bcn")
		return QVariant(int(section + 1)) # TODO: what's this?????
	
	def rowCount(self, index=QModelIndex()):
		"""
		This function is mandatory for the model to work.
		"""
		if not index.isValid():
			return len(self.channels)
		return 0 # <---channels have no children
	
	def columnCount(self, index=QModelIndex()):
		"""
		This function is mandatory for the model to work.
		"""
		return 4
		
	def setData(self, index, value, role=Qt.EditRole):
		if index.isValid() and 0 <= index.row() < len(self.channels):
			self.channels[index.row()][index.column()] = value
			self.dataChanged = True
			self.emit(SIGNAL("dataChanged(QModelIndex,QModelIndex)"),
						index, index)
			return True
		return False
	
	def clickedChannel(self, index):
		return int(self.channels[index.row()][0])
	
	def append(self, channel):
		"""
		Adds one packet at end of the packets list
		"""
		self.beginInsertRows(QModelIndex(), len(self.channels), len(self.channels) + 1)
		self.channels.append(channel)
		self.dataChanged = True
		self.endInsertRows()
	
	def clear(self):
		"""
		Clears the packets list
		"""
		self.beginRemoveRows(QModelIndex(), 0, len(self.channels))
		self.packets = []
		self.endRemoveRows()
	
	def load(self, fh):
		"""
		Load packets from given file handler
		"""
		pass
	
	def save(self, fh):
		"""
		This function writes collected data into a fh file in .154 format
		"""
		pass