# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'src/ui/dialogNodes.ui'
#
# Created: Sat Sep 12 13:22:06 2009
#      by: PyQt4 UI code generator 4.5.4
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

class Ui_dialogNodes(object):
    def setupUi(self, dialogNodes):
        dialogNodes.setObjectName("dialogNodes")
        dialogNodes.resize(630, 317)
        self.verticalLayout = QtGui.QVBoxLayout(dialogNodes)
        self.verticalLayout.setObjectName("verticalLayout")
        self.tableView = QtGui.QTableView(dialogNodes)
        self.tableView.setEditTriggers(QtGui.QAbstractItemView.DoubleClicked|QtGui.QAbstractItemView.EditKeyPressed)
        self.tableView.setProperty("showDropIndicator", QtCore.QVariant(False))
        self.tableView.setGridStyle(QtCore.Qt.DotLine)
        self.tableView.setObjectName("tableView")
        self.tableView.horizontalHeader().setDefaultSectionSize(170)
        self.tableView.horizontalHeader().setStretchLastSection(True)
        self.tableView.verticalHeader().setVisible(False)
        self.verticalLayout.addWidget(self.tableView)
        self.buttonBox = QtGui.QDialogButtonBox(dialogNodes)
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Cancel|QtGui.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName("buttonBox")
        self.verticalLayout.addWidget(self.buttonBox)

        self.retranslateUi(dialogNodes)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL("accepted()"), dialogNodes.accept)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL("rejected()"), dialogNodes.reject)
        QtCore.QMetaObject.connectSlotsByName(dialogNodes)

    def retranslateUi(self, dialogNodes):
        dialogNodes.setWindowTitle(QtGui.QApplication.translate("dialogNodes", "Dialog", None, QtGui.QApplication.UnicodeUTF8))

