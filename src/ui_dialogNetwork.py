# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'src/ui/dialogNetwork.ui'
#
# Created: Mon Sep 14 19:55:08 2009
#      by: PyQt4 UI code generator 4.5.4
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

class Ui_dialogNetwork(object):
    def setupUi(self, dialogNetwork):
        dialogNetwork.setObjectName("dialogNetwork")
        dialogNetwork.resize(640, 439)
        self.verticalLayout = QtGui.QVBoxLayout(dialogNetwork)
        self.verticalLayout.setObjectName("verticalLayout")
        self.scrollArea = QtGui.QScrollArea(dialogNetwork)
        self.scrollArea.setFrameShape(QtGui.QFrame.StyledPanel)
        self.scrollArea.setFrameShadow(QtGui.QFrame.Sunken)
        self.scrollArea.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOn)
        self.scrollArea.setWidgetResizable(True)
        self.scrollArea.setObjectName("scrollArea")
        self.scrollAreaWidgetContents = QtGui.QWidget(self.scrollArea)
        self.scrollAreaWidgetContents.setGeometry(QtCore.QRect(0, 0, 609, 394))
        self.scrollAreaWidgetContents.setObjectName("scrollAreaWidgetContents")
        self.scrollArea.setWidget(self.scrollAreaWidgetContents)
        self.verticalLayout.addWidget(self.scrollArea)
        self.buttonBox = QtGui.QDialogButtonBox(dialogNetwork)
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName("buttonBox")
        self.verticalLayout.addWidget(self.buttonBox)

        self.retranslateUi(dialogNetwork)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL("accepted()"), dialogNetwork.accept)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL("rejected()"), dialogNetwork.reject)
        QtCore.QMetaObject.connectSlotsByName(dialogNetwork)

    def retranslateUi(self, dialogNetwork):
        dialogNetwork.setWindowTitle(QtGui.QApplication.translate("dialogNetwork", "Network structure", None, QtGui.QApplication.UnicodeUTF8))

import icons_rc
