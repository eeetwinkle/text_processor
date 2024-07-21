import sys
from PyQt5 import QtWidgets
from QtMainWindow import Ui_color
from QtSearchWindow import Ui_QtSearchWindow
from QtReplaceWindow import Ui_QtReplaceWindow
from QtStyles import Ui_Form

class MainWindow(QtWidgets.QMainWindow, Ui_color):
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.search_window = SearchWindow()
        self.replace_window = ReplaceWindow()
        self.style_window = StyleWindow()
        self.search.clicked.connect(self.open_search_window)
        self.replace.clicked.connect(self.open_replace_window)
        self.style.clicked.connect(self.open_style_window)

    def open_search_window(self):
        self.search_window.show()

    def open_replace_window(self):
        self.replace_window.show()

    def open_style_window(self):
        self.style_window.show()

class SearchWindow(QtWidgets.QWidget, Ui_QtSearchWindow):
    def __init__(self):
        super().__init__()
        self.setupUi(self)

class ReplaceWindow(QtWidgets.QWidget, Ui_QtReplaceWindow):
    def __init__(self):
        super().__init__()
        self.setupUi(self)

class StyleWindow(QtWidgets.QWidget, Ui_Form):
    def __init__(self):
        super().__init__()
        self.setupUi(self)


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    main_window = MainWindow()
    main_window.show()
    sys.exit(app.exec_())
