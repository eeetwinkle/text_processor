from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_QtSearchWindow(object):
    def setupUi(self, QtSearchWindow):
        QtSearchWindow.setObjectName("QtSearchWindow")
        QtSearchWindow.resize(500, 200)
        self.pushButton_search = QtWidgets.QPushButton(QtSearchWindow)
        self.pushButton_search.setGeometry(QtCore.QRect(390, 160, 93, 28))
        self.pushButton_search.setObjectName("pushButton_search")
        self.layoutWidget = QtWidgets.QWidget(QtSearchWindow)
        self.layoutWidget.setGeometry(QtCore.QRect(20, 30, 461, 24))
        self.layoutWidget.setObjectName("layoutWidget")
        self.horizontalLayout = QtWidgets.QHBoxLayout(self.layoutWidget)
        self.horizontalLayout.setContentsMargins(0, 0, 0, 0)
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.label = QtWidgets.QLabel(self.layoutWidget)
        self.label.setObjectName("label")
        self.horizontalLayout.addWidget(self.label)
        self.lineEdit_search = QtWidgets.QLineEdit(self.layoutWidget)
        self.lineEdit_search.setObjectName("lineEdit_search")
        self.horizontalLayout.addWidget(self.lineEdit_search)
        self.layoutWidget1 = QtWidgets.QWidget(QtSearchWindow)
        self.layoutWidget1.setGeometry(QtCore.QRect(20, 70, 162, 72))
        self.layoutWidget1.setObjectName("layoutWidget1")
        self.verticalLayout = QtWidgets.QVBoxLayout(self.layoutWidget1)
        self.verticalLayout.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout.setObjectName("verticalLayout")
        self.label_2 = QtWidgets.QLabel(self.layoutWidget1)
        self.label_2.setObjectName("label_2")
        self.verticalLayout.addWidget(self.label_2)
        self.checkBox_register = QtWidgets.QCheckBox(self.layoutWidget1)
        self.checkBox_register.setObjectName("checkBox_register")
        self.verticalLayout.addWidget(self.checkBox_register)
        self.checkBox_entirely = QtWidgets.QCheckBox(self.layoutWidget1)
        self.checkBox_entirely.setObjectName("checkBox_entirely")
        self.verticalLayout.addWidget(self.checkBox_entirely)

        self.retranslateUi(QtSearchWindow)
        QtCore.QMetaObject.connectSlotsByName(QtSearchWindow)

    def retranslateUi(self, QtSearchWindow):
        _translate = QtCore.QCoreApplication.translate
        QtSearchWindow.setWindowTitle(_translate("QtSearchWindow", "Form"))
        self.pushButton_search.setText(_translate("QtSearchWindow", "Найти далее"))
        self.label.setText(_translate("QtSearchWindow", "Найти:"))
        self.label_2.setText(_translate("QtSearchWindow", "Параметры поиска:"))
        self.checkBox_register.setText(_translate("QtSearchWindow", "Учитывать регистр"))
        self.checkBox_entirely.setText(_translate("QtSearchWindow", "Только слово целиком"))


if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    QtSearchWindow = QtWidgets.QWidget()
    ui = Ui_QtSearchWindow()
    ui.setupUi(QtSearchWindow)
    QtSearchWindow.show()
    sys.exit(app.exec_())
