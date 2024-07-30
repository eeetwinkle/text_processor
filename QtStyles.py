from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_Form(object):
    def setupUi(self, Form):
        Form.setObjectName("Form")
        Form.resize(492, 385)
        self.line_2 = QtWidgets.QFrame(Form)
        self.line_2.setGeometry(QtCore.QRect(20, 260, 441, 16))
        self.line_2.setFrameShape(QtWidgets.QFrame.HLine)
        self.line_2.setFrameShadow(QtWidgets.QFrame.Sunken)
        self.line_2.setObjectName("line_2")
        self.gridLayoutWidget_2 = QtWidgets.QWidget(Form)
        self.gridLayoutWidget_2.setGeometry(QtCore.QRect(20, 280, 211, 121))
        self.gridLayoutWidget_2.setObjectName("gridLayoutWidget_2")
        self.gridLayout_2 = QtWidgets.QGridLayout(self.gridLayoutWidget_2)
        self.gridLayout_2.setContentsMargins(0, 0, 0, 0)
        self.gridLayout_2.setObjectName("gridLayout_2")
        self.label = QtWidgets.QLabel(self.gridLayoutWidget_2)
        self.label.setObjectName("label")
        self.gridLayout_2.addWidget(self.label, 0, 1, 1, 1)
        self.new_style = QtWidgets.QPushButton(self.gridLayoutWidget_2)
        self.new_style.setText("")
        self.new_style.setObjectName("new_style")
        self.gridLayout_2.addWidget(self.new_style, 0, 0, 1, 1)
        self.label_3 = QtWidgets.QLabel(self.gridLayoutWidget_2)
        self.label_3.setObjectName("label_3")
        self.gridLayout_2.addWidget(self.label_3, 1, 1, 1, 1)
        self.save = QtWidgets.QPushButton(self.gridLayoutWidget_2)
        self.save.setMinimumSize(QtCore.QSize(87, 32))
        self.save.setText("")
        self.save.setObjectName("save")
        self.gridLayout_2.addWidget(self.save, 1, 0, 1, 1)
        self.scrollArea = QtWidgets.QScrollArea(Form)
        self.scrollArea.setGeometry(QtCore.QRect(20, 30, 391, 211))
        self.scrollArea.setWidgetResizable(True)
        self.scrollArea.setObjectName("scrollArea")
        self.scrollAreaWidgetContents = QtWidgets.QWidget()
        self.scrollAreaWidgetContents.setGeometry(QtCore.QRect(0, 0, 389, 209))
        self.scrollAreaWidgetContents.setObjectName("scrollAreaWidgetContents")
        self.verticalScrollBar = QtWidgets.QScrollBar(self.scrollAreaWidgetContents)
        self.verticalScrollBar.setGeometry(QtCore.QRect(10, 9, 21, 191))
        self.verticalScrollBar.setOrientation(QtCore.Qt.Vertical)
        self.verticalScrollBar.setObjectName("verticalScrollBar")
        self.scrollArea.setWidget(self.scrollAreaWidgetContents)

        self.retranslateUi(Form)
        QtCore.QMetaObject.connectSlotsByName(Form)

    def retranslateUi(self, Form):
        _translate = QtCore.QCoreApplication.translate
        Form.setWindowTitle(_translate("Form", "Form"))
        self.label.setText(_translate("Form", "Создать стиль"))
        self.label_3.setText(_translate("Form", "Применить стиль "))


if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    Form = QtWidgets.QWidget()
    ui = Ui_Form()
    ui.setupUi(Form)
    Form.show()
    sys.exit(app.exec_())
