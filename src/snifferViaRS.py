# -*- coding: utf-8 -*-
"""
This module is responsible for communication with hardware sniffer via serial port.
There is also some serial-related stuff here (such as scan for ports etc...)
"""
import serial
from PyQt4.QtCore import QObject, QTimer, SIGNAL
from PyQt4.QtGui import QMessageBox
import settings

class Sniffer(serial.Serial, QObject):
	def __init__(self): 
		try:
			serial.Serial.__init__(self, settings.port['number'], settings.port['baudrate'], timeout = 0.01)
		except serial.serialutil.SerialException, e:
			msg = QMessageBox()
			msg.setText("Error while trying to connect with sniffer.")
			msg.setInformativeText(e.message)
			msg.setStandardButtons(QMessageBox.Ok)
			msg.setDefaultButton(QMessageBox.Ok)
			msg.exec_()
		else:
			QObject.__init__(self)
			self.timer1 = QTimer()	# timer object
			self.timer1.connect(self.timer1, SIGNAL("timeout()"), self.read_line)
	
	def write(self, data):
		print data
		serial.Serial.write(self, data) 
	
	def disconnect_(self):
		self.close()
	
	def start_reading(self):
		self.timer1.start(10)
	
	def stop_reading(self):
		self.timer1.stop()
	
	def read_line(self):
		rx = self.readline(eol='\n')
		if len(rx) > 0:
			self.emit(SIGNAL('rx'), rx)
			
	# ==== commands: =============
	
	def cmd_sniff(self, channel):
		self.write('X')
		self.write('SN')
		self.write(str(channel))
	
	def cmd_stop(self):
		self.write('X')
		self.write('ST')
	
	def cmd_scan_channel(self, channel):
		self.write('X')
		self.write('SC')
		self.write(str(channel))
	
	def scan_serial(self):
		"""
		Scan for available ports. return a list of tuples (num, name).
		"""
		available = []
		for i in range(256):
			try:
				s = serial.Serial(i)
				available.append( (i, s.name))
				s.close()   # explicit close 'cause of delayed GC in java
			except serial.SerialException:
				pass
			return available