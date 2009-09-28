# -*- coding: utf-8 -*-
"""
This is the ZigBeeSniffer application, it is designed to work with
the 802.15.4 sniffer hardware based on PicDem-Z board and CC2420 transciever.
"""

# TODO: zrobic wyjatek zamykajacy port szeregowy w razie czego,
# TODO: zrobic komunikat kiedy nie ma dostepnych portow

import datetime
from PyQt4 import QtCore, QtGui
import ui_snifferMainWindow, ui_dialogNodes
import snifferViaRS
from dialogNetwork import DialogNetwork
from snifferData.packet import Packet
from snifferData.packets import PacketsModel, PacketsDelegate
from snifferData.channels import ChannelsModel
from snifferData.packetDetails import DetailsModel, updatePacketDetails
from snifferData.constants import *


#possible states of program:
NONE, STOP, SCAN_CHANNELS, SCAN_CHANNEL, SNIFF = range(5)


class SnifferWindow(QtGui.QMainWindow, ui_snifferMainWindow.Ui_SnifferMainWindow):
	"""
	Main window class.
	"""
	state = NONE  # let's say it's finite state machine
	filename = None
	
	def __init__(self, parent=None):
		super(SnifferWindow, self).__init__(parent)
		# GUI things... 
		self.setupUi(self)
		self.iconStop = QtGui.QIcon()
		self.iconStop.addPixmap(QtGui.QPixmap(":/icons/media-playback-stop.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
		self.iconStart = QtGui.QIcon()
		self.iconStart.addPixmap(QtGui.QPixmap(":/icons/media-playback-start.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
		self.update_ui()
		self.btnNew.setDefaultAction(self.actionNew)
		self.btnImport.setDefaultAction(self.actionImport)
		self.btnSave.setDefaultAction(self.actionSave)
		self.btnSniff.setDefaultAction(self.actionSniff)
		self.btnScanChannel.setDefaultAction(self.actionScan_channel)
		self.btnScanChannels.setDefaultAction(self.actionScan_channels)
		self.btnNameNodes.setDefaultAction(self.actionName_nodes)
		self.btnStatistics.setDefaultAction(self.actionStatistics)
		
		# data collecting and presenting...
		self.packets = PacketsModel()
		self.channels = ChannelsModel()
		self.details = DetailsModel()
		self.treePackets.setModel(self.packets)
		self.treePackets.setItemDelegate(PacketsDelegate(self))
		self.treeChannels.setModel(self.channels)
		self.connect(self.packets, QtCore.SIGNAL("changed"), self.update_ui)
		self.connect(self.packets.nodes, QtCore.SIGNAL("changed"), self.update_ui)
		self.sniffer = snifferViaRS.Sniffer()
		self.connect(self.sniffer, QtCore.SIGNAL("rx"), self.readserial)
		self.channel = 0
	
	def closeEvent(self, event):
		"""
		This event takes care about unsaved data and running serial transmission while user wants to exit app.
		"""
		if self.state not in (NONE, STOP):
			reply = QtGui.QMessageBox.question(self, 'Close ZigBee Snifer application',
				"Sniffer is working. Are you sure to quit?", QtGui.QMessageBox.Yes, QtGui.QMessageBox.No)
			if reply == QtGui.QMessageBox.Yes:
				self.sniffer.disconnect_()
				event.accept()
			else:
				event.ignore()
		elif self.packets.changed() or self.packets.nodes.changed():
			reply = QtGui.QMessageBox.question(self, 'Close ZigBee Snifer application',
				"There is unsaved data in current sniff log. Are you sure to quit?", QtGui.QMessageBox.Yes, QtGui.QMessageBox.No)
			if reply == QtGui.QMessageBox.Yes:
				event.accept()
			else:
				event.ignore()
		else:
			event.accept()
	
	def update_ui(self):
		"""
		Depending on the state of (so called here) finite state machine, 
		this function sets the widgets on main window form (enables and disables, etc.)
		"""
		if self.state == STOP:
			self.actionScan_channels.setText('Scan channels')
			self.actionScan_channels.setToolTip('Scan channels')
			self.actionScan_channel.setText('Scan channel')
			self.actionScan_channel.setToolTip('Scan channel')
			self.actionSniff.setText('Sniff')
			self.actionSniff.setToolTip('Sniff')
			self.actionSniff.setIcon(self.iconStart)
			self.enable_controls(self.actionNew, self.actionImport, self.actionScan_channels,
								self.treeChannels)
			if self.packets.changed() or self.packets.nodes.changed():
				self.actionSave.setEnabled(True)
			else:
				self.actionSave.setDisabled(True)
			if self.channel: #if there is any channel selected....
				self.enable_controls(self.actionScan_channel, self.actionSniff)
			if int(self.packets.rowCount()) > 0:
				self.setStatusTip('Stopped, ready. Packets recieved: ' + str(self.packets.rowCount()))
				self.enable_controls(self.actionStatistics, self.actionName_nodes)
				
		if self.state in (SCAN_CHANNELS, SCAN_CHANNEL, SNIFF):
			#turn off all buttons
			self.disable_controls(self.actionNew, self.actionImport, self.actionSave,
						self.actionStatistics, self.actionName_nodes, self.actionScan_channels, 
						self.actionScan_channel, self.actionSniff, self.treeChannels)
			
		if self.state == SCAN_CHANNELS:
			self.actionScan_channels.setText('Stop scanning channels')
			self.actionScan_channels.setToolTip('Stop scanning channels')
			self.setStatusTip('Scanning channels...')
			self.actionScan_channels.setEnabled(True)
		elif self.state == SCAN_CHANNEL:
			self.actionScan_channel.setText('Stop scanning channel %i' % self.channel)
			self.actionScan_channel.setToolTip('Stop scanning channel %i' % self.channel)
			self.setStatusTip('Scanning channel %i' % self.channel) 
			self.actionScan_channel.setEnabled(True)
		elif self.state == SNIFF:
			self.actionSniff.setIcon(self.iconStop)
			self.actionSniff.setText('Stop sniffing')
			self.actionSniff.setToolTip('Stop sniffing')
			self.setStatusTip('Sniffing on channel %i' % self.channel)
			self.actionSniff.setEnabled(True)
	
	def enable_controls(self, *args, **kwargs):
		"""
		Enable/disable all widgets given.
		Widgets are in args, value is in kwargs (e.g. value=True)
		"""
		if not kwargs.has_key('value'):
			kwargs['value'] = True
		for widget in args:
			widget.setEnabled(kwargs['value'])
			
	def disable_controls(self, *args):
		"""
		Disable all given widgets
		"""
		self.enable_controls(*args, value=False)
	
	def on_actionAbout_sniffer_activated(self):
		pass # TODO: about
	
	@QtCore.pyqtSignature("")
	def on_actionSniff_activated(self):
		"""
		Start/stop sniffing packets on selected channel.
		"""
		if self.state in (STOP, NONE):
			self.sniffer.start_reading()
			self.sniffer.cmd_sniff(self.channel)
			self.state = SNIFF
		elif self.state == SNIFF:
			self.sniffer.cmd_stop() 
			self.sniffer.stop_reading()
			self.state = STOP
		self.update_ui()
		
	@QtCore.pyqtSignature("")
	def on_actionScan_channel_activated(self):
		"""
		Start/stop scanning selected channel.
		"""
		if self.state == SCAN_CHANNEL:
			self.sniffer.cmd_stop() 
			self.sniffer.stop_reading()
			self.state = STOP
		else:
			self.sniffer.start_reading()
			self.sniffer.cmd_scan_channel(self.channel) 
			self.state = SCAN_CHANNEL
		self.update_ui()
	
	@QtCore.pyqtSignature("")
	def on_actionScan_channels_activated(self):
		"""
		Start/stop scanning channels.
		"""
		if self.state == SCAN_CHANNELS:
			self.timerScan.stop()
			self.sniffer.cmd_stop()
			self.sniffer.stop_reading()
			self.channel = self.rememberChannel
			self.state = STOP
		else:
			self.rememberChannel = int(self.channel)
			self.channel = 10 # it'll be incremented, so it'll start from 11
			self.timerScan = QtCore.QTimer()
			self.timerScan.connect(self.timerScan, QtCore.SIGNAL("timeout()"), self.scan_channels)
			self.scan_channels()
			self.timerScan.start(2500)
			self.state = SCAN_CHANNELS
		self.update_ui()
	
	@QtCore.pyqtSignature("")
	def on_actionNew_activated(self):
		"""
		Clear collected data and start everything from scratch.
		"""
		self.packets.clear()
		self.packets.nodes.clear()
		self.state = STOP
		self.update_ui()
	
	@QtCore.pyqtSignature("")
	def on_actionImport_activated(self):
		"""
		Import data from file.
		"""
		fname = '.'
		fname = QtGui.QFileDialog.getOpenFileName(self,
							'ZigBee Sniffer - Import a log file', fname,
							'IEEE 802.15.4 log files (*.154)')
		
		if fname: # if file dialog not rejected, picked some file
			with open(fname, 'r') as fh:
				self.on_actionNew_activated() # clear previous data
				self.packets.load(fh)
				self.state = STOP
				self.update_ui()
	
	@QtCore.pyqtSignature("")
	def on_actionSave_activated(self):
		"""
		Save collected data into a file.
		"""
		fname = '.'
		fname = QtGui.QFileDialog.getSaveFileName(self,
							'ZigBee Sniffer - save log file', fname,
							'IEEE 802.15.4 log files (*.154)')
		if fname: # if file dialog not rejected, picked some file
			if '.' not in fname: fname += '.154'
			with open(fname, 'w') as fh:
				self.packets.save(fh)
				self.update_ui()
	
	def on_actionName_nodes_activated(self):
		self.dlgNodes = DialogNodes(self.packets.nodes)
		self.dlgNodes.show()
	
	def on_actionStatistics_activated(self):
		stats = """Frames recieved: {frames_count}
					Invalid frames: {invalid_count}
					Error rate: {error_rate} %
					
					Nodes: {nodes_count}
					
					Beacon frames: {bcn_count}
					Data frames: {data_count}
					Ack. frames:  {ack_count}
					Command frames: {cmd_count}""".format(
					frames_count = self.packets.rowCount(),
					invalid_count = self.packets.invlaid_count(),
					error_rate = round(self.packets.error_rate(), 1),
					nodes_count = self.packets.nodes.rowCount(),
					bcn_count = self.packets.type_count(TYPE_BCN),
					data_count = self.packets.type_count(TYPE_DATA),
					ack_count = self.packets.type_count(TYPE_ACK),
					cmd_count = self.packets.type_count(TYPE_CMD)
					)
					
		for cmd in (CMD_ASS_REQ, CMD_ASS_RESP, CMD_DIS_NOT, CMD_DAT_REQ,
					CMD_PAN_ID_CON, CMD_ORP_NOT, CMD_BCN_REQ, CMD_CRD_REL, CMD_GTS_REQ):
			if self.packets.type_count(TYPE_CMD, cmd):
				stats += '\r\n - {0}s: {1}'.format(cmd, self.packets.type_count(TYPE_CMD, cmd))
		
		QtGui.QMessageBox.information(self, 'Statistics', stats.replace('\t', ''), QtGui.QMessageBox.Yes)
					
	#@QtCore.pyqtSignature("")
	def on_treePackets_activated(self, index):
		"""
		This 'slot' updates detailed view of current selected packet.
		"""
		#self.details.setPacket(self.packets.getPacket(index))
		#a = QtGui.QMessageBox.question(self, u'podgląd',
		#str(index.row()), QtGui.QMessageBox.Yes, QtGui.QMessageBox.No)
		updatePacketDetails(self.treeDetails, 
										self.packets.packets[index.row()])
		self.treeDetails.expandAll()
		self.treeDetails.resizeColumnToContents(0)
		self.treeDetails.resizeColumnToContents(1)
	
	def on_actionNetwork_structure_activated(self):
		self.dlgNetwork = DialogNetwork(self.nodes)
		self.dlgNetwork.show()
	
	def on_treeDetails_activated(self, index):
		pass
		#if hasattr(index, 'row'):
		#	a = QtGui.QMessageBox.question(self, u'podgląd',
		#		str(index.row())+ ' '+str(index.parent.row()), QtGui.QMessageBox.Yes, QtGui.QMessageBox.No)
	
	#@QtCore.pyqtSignature("")
	def on_treeChannels_activated(self, index):
		"""
		We make sure here that there is any channel selected to sniff or to scan.
		"""
		self.channel = self.channels.clickedChannel(index)
		if self.state in (NONE, STOP):
			self.enable_controls(self.actionSniff, self.actionScan_channel)
	
	def readserial(self, rx):
		"""
		This function is responsible for sending recieved data to right objects depending on applications state.
		"""
		print 'Sniffer: %s' % rx.rstrip()
		if rx[:2] == 'F:': #if this was a frame
			load = rx.rstrip()[2:].split(',')[1:]
			load = [int(x) for x in load]
			timee = datetime.datetime.now()
			m = '000' + str(timee.microsecond / 1000)
			m = m[-3:]
			timee = (str(timee.hour), 
					str(timee.minute), 
					str(timee.second), 
					m)					# format the time "H,M,S,m"
			packet = Packet(load, timee)
			
			if self.state == SNIFF:
				self.packets.append(packet)
			elif self.state in (SCAN_CHANNEL, SCAN_CHANNELS):
				if packet.frameType == TYPE_BCN:
					bcnIndex = self.channels.index(self.channel-11, 3)
					bcn = int(self.channels.data(bcnIndex)) + 1
					self.channels.setData(bcnIndex, bcn)
				lqiIndex = self.channels.index(self.channel-11, 2)
				lqi = int(self.channels.data(lqiIndex).toString())
				lqi = average(lqi, int(packet.LQI[:-1]))
				lqi = str(lqi)
				self.channels.setData(lqiIndex, lqi)
	
	def scan_channels(self):
		"""
		This function is called by timer. Its job is to scan next channel each time it's called.
		"""
		if self.channel < 26:
			self.sniffer.stop_reading()
			self.channel += 1
			self.sniffer.start_reading()
			self.sniffer.cmd_scan_channel(self.channel)
		else:
			if self.state == SCAN_CHANNELS: #check for sure
				#this should stop the scan:
				self.actionScan_channels.emit(QtCore.SIGNAL("activated()"))
	

def average(*values):
	"""Computes the arithmetic mean of a list of numbers.
	>>> print average([20, 30, 70])
	40
	"""
	return int(sum(values) / len(values))


class DialogNodes(QtGui.QDialog, ui_dialogNodes.Ui_dialogNodes):
	"""
	
	"""
	def __init__(self, model, parent=None):
		super(DialogNodes, self).__init__(parent)
		self.setupUi(self)
		self.tableView.setModel(model)


	
if __name__ == "__main__":
	import sys
	app = QtGui.QApplication(sys.argv)
	form = SnifferWindow()
	form.show()
	app.exec_()
	