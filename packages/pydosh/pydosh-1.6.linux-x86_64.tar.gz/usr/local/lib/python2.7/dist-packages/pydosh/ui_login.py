# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'ui/login.ui'
#
# Created: Thu May  9 06:32:33 2013
#      by: PyQt4 UI code generator 4.10
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    def _fromUtf8(s):
        return s

try:
    _encoding = QtGui.QApplication.UnicodeUTF8
    def _translate(context, text, disambig):
        return QtGui.QApplication.translate(context, text, disambig, _encoding)
except AttributeError:
    def _translate(context, text, disambig):
        return QtGui.QApplication.translate(context, text, disambig)

class Ui_Login(object):
    def setupUi(self, Login):
        Login.setObjectName(_fromUtf8("Login"))
        Login.resize(224, 246)
        self.gridLayout_2 = QtGui.QGridLayout(Login)
        self.gridLayout_2.setObjectName(_fromUtf8("gridLayout_2"))
        self.standardOptionsBox = QtGui.QGroupBox(Login)
        self.standardOptionsBox.setCheckable(False)
        self.standardOptionsBox.setObjectName(_fromUtf8("standardOptionsBox"))
        self.gridLayout_3 = QtGui.QGridLayout(self.standardOptionsBox)
        self.gridLayout_3.setObjectName(_fromUtf8("gridLayout_3"))
        self.label = QtGui.QLabel(self.standardOptionsBox)
        self.label.setObjectName(_fromUtf8("label"))
        self.gridLayout_3.addWidget(self.label, 2, 0, 1, 1)
        self.hostnameEdit = QtGui.QLineEdit(self.standardOptionsBox)
        self.hostnameEdit.setObjectName(_fromUtf8("hostnameEdit"))
        self.gridLayout_3.addWidget(self.hostnameEdit, 2, 1, 1, 1)
        self.label_2 = QtGui.QLabel(self.standardOptionsBox)
        self.label_2.setObjectName(_fromUtf8("label_2"))
        self.gridLayout_3.addWidget(self.label_2, 3, 0, 1, 1)
        self.databaseEdit = QtGui.QLineEdit(self.standardOptionsBox)
        self.databaseEdit.setObjectName(_fromUtf8("databaseEdit"))
        self.gridLayout_3.addWidget(self.databaseEdit, 3, 1, 1, 1)
        self.label_5 = QtGui.QLabel(self.standardOptionsBox)
        self.label_5.setObjectName(_fromUtf8("label_5"))
        self.gridLayout_3.addWidget(self.label_5, 4, 0, 1, 1)
        self.portSpinBox = QtGui.QSpinBox(self.standardOptionsBox)
        self.portSpinBox.setMaximum(99999)
        self.portSpinBox.setObjectName(_fromUtf8("portSpinBox"))
        self.gridLayout_3.addWidget(self.portSpinBox, 4, 1, 1, 1)
        self.label_4 = QtGui.QLabel(self.standardOptionsBox)
        self.label_4.setObjectName(_fromUtf8("label_4"))
        self.gridLayout_3.addWidget(self.label_4, 1, 0, 1, 1)
        self.passwordEdit = QtGui.QLineEdit(self.standardOptionsBox)
        self.passwordEdit.setObjectName(_fromUtf8("passwordEdit"))
        self.gridLayout_3.addWidget(self.passwordEdit, 1, 1, 1, 1)
        self.label_3 = QtGui.QLabel(self.standardOptionsBox)
        self.label_3.setObjectName(_fromUtf8("label_3"))
        self.gridLayout_3.addWidget(self.label_3, 0, 0, 1, 1)
        self.usernameEdit = QtGui.QLineEdit(self.standardOptionsBox)
        self.usernameEdit.setObjectName(_fromUtf8("usernameEdit"))
        self.gridLayout_3.addWidget(self.usernameEdit, 0, 1, 1, 1)
        self.gridLayout_2.addWidget(self.standardOptionsBox, 0, 0, 1, 3)
        self.connectionButton = QtGui.QPushButton(Login)
        self.connectionButton.setObjectName(_fromUtf8("connectionButton"))
        self.gridLayout_2.addWidget(self.connectionButton, 1, 1, 1, 1)
        self.closeButton = QtGui.QPushButton(Login)
        self.closeButton.setObjectName(_fromUtf8("closeButton"))
        self.gridLayout_2.addWidget(self.closeButton, 1, 2, 1, 1)
        self.label.setBuddy(self.hostnameEdit)
        self.label_2.setBuddy(self.databaseEdit)
        self.label_4.setBuddy(self.passwordEdit)
        self.label_3.setBuddy(self.usernameEdit)

        self.retranslateUi(Login)
        QtCore.QMetaObject.connectSlotsByName(Login)
        Login.setTabOrder(self.connectionButton, self.closeButton)
        Login.setTabOrder(self.closeButton, self.usernameEdit)
        Login.setTabOrder(self.usernameEdit, self.passwordEdit)
        Login.setTabOrder(self.passwordEdit, self.hostnameEdit)
        Login.setTabOrder(self.hostnameEdit, self.databaseEdit)
        Login.setTabOrder(self.databaseEdit, self.portSpinBox)

    def retranslateUi(self, Login):
        Login.setWindowTitle(_translate("Login", "Login", None))
        self.standardOptionsBox.setTitle(_translate("Login", "Database", None))
        self.label.setText(_translate("Login", "hostname", None))
        self.label_2.setText(_translate("Login", "database", None))
        self.label_5.setText(_translate("Login", "port", None))
        self.label_4.setText(_translate("Login", "password", None))
        self.label_3.setText(_translate("Login", "username", None))
        self.connectionButton.setText(_translate("Login", "Connect", None))
        self.closeButton.setText(_translate("Login", "&Close", None))

import pydosh_rc
