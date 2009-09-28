'''
Created on 2009-09-24

@author: sylwek
'''
from PyQt4.QtCore import QObject, SIGNAL

class Klasa1(object):
	def __init__(self):
		self.qobject = QObject()
		self.emit = self.qobject.emit
	
	def funkcja(self, arg):
		self.emit(SIGNAL("sygnal"), arg)

class Klasa2(QObject):
	def __init__(self):
		QObject.__init__(self)
	
	def funkcja(self, arg):
		self.emit(SIGNAL("sygnal"), arg)

def dupa(arg):
	print arg

obj1 = Klasa1()
obj2 = Klasa2()

#QObject.connect(obj1, SIGNAL("sygnal"), dupa)
QObject.connect(obj2, SIGNAL("sygnal"), dupa)

obj2.funkcja(222)
obj1.funkcja(111)

print ":-)"
