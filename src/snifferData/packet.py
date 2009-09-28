# -*- coding: utf-8 -*-

from mac import Mac

class Packet(Mac):
	"""
	This is a class of packet objects.
	Decoding of MAC fields is done at __init__ using packet load.
	"""
	def __init__(self, load, time):
		super(Packet, self).__init__(load)
		self.load = load
		self.time = time
	
	def __repr__(self):
		return ','.join(self.load)