'''
Created on 2009-09-14

@author: sylwek
'''
from ui_dialogNetwork import Ui_dialogNetwork
from PyQt4 import QtCore
from PyQt4.QtGui import QDialog, QLabel, QPixmap, QWidget, QFont

class DialogNetwork(QDialog, Ui_dialogNetwork):
	'''
	This is a dialog window form. We fill this form with network structure here.
	'''

	def __init__(self, nodes):
		'''
		Constructor
		'''
		super(DialogNetwork, self).__init__()
		self.setupUi(self)
		
		icon = QPixmap(":/icons/network-wireless.png")
		
		x = 30
		y = 30
		self.nwk_nodes = []
		for node in nodes.nodes:
			self.nwk_nodes.append(NetworkNode(self.scrollArea, node, icon, x, y))
			y += 90
		


class NetworkNode(QWidget):
	'''
	This class is a widget containing picture and label(s) describing network node
	'''
	
	def __init__(self, parent, node, icon, x=0, y=0):
		'''
		The node is a Node object (from snifferData.nodes),
		icon is a QPixmap object
		'''
		super(NetworkNode, self).__init__(parent)
		
		self.width_ = 130
		self.height_ = 81
		font = QFont()
		font.setFamily("DejaVu Sans Mono")
		font.setPointSize(9)
		
		self.lbl_icon = QLabel(self)
		self.lbl_icon.setGeometry(QtCore.QRect(50, 0, 48, 48))
		self.lbl_icon.setObjectName("lbl_icon")
		self.lbl_icon.setPixmap(icon)
		
		self.lbl_name = QLabel(self)
		self.lbl_name.setGeometry(QtCore.QRect(0, 50, self.width_, 16))
		self.lbl_name.setObjectName("lbl_name")
		self.lbl_name.setAlignment(QtCore.Qt.AlignCenter)
		self.lbl_name.setText(node.name)
		self.lbl_name.setFont(font)
		
		
		self.lbl_addr = QLabel(self)
		self.lbl_addr.setGeometry(QtCore.QRect(0, 65, self.width_, 16))
		self.lbl_addr.setObjectName("lbl_addr")
		self.lbl_addr.setAlignment(QtCore.Qt.AlignCenter)
		self.lbl_addr.setText('<span style="color:#888">%s</span>' % node.address)
		self.lbl_addr.setFont(font)
		
		self.setGeometry(QtCore.QRect(x, y, self.width_, self.height_))