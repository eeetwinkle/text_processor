import sys
from PyQt5 import QtWidgets, QtGui, QtCore
from QtMainWindow import Ui_color
from QtSearchWindow import Ui_QtSearchWindow
from QtReplaceWindow import Ui_QtReplaceWindow
from QtStyles import Ui_Form
from QtNewStyle import Ui_QtNewStyleWindow
from PyQt5.QtGui import QTextCursor, QTextBlockFormat


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

        self.font.currentFontChanged.connect(self.update_font)
        self.font_size.currentIndexChanged.connect(self.update_font_size)

        self.bold.clicked.connect(self.toggle_bold)
        self.italic.clicked.connect(self.toggle_italic)
        self.underlined.clicked.connect(self.toggle_underlined)

        self.update_font()
        self.update_font_size()

        self.bold_active = False
        self.italic_active = False
        self.underlined_active = False

        self.indent_value = 0
        self.reduce_indentation.clicked.connect(self.update_indent)
        self.increase_indentation.clicked.connect(self.update_indent)

        self.size_interval.currentTextChanged.connect(self.change_line_spacing)

    # Меняет межстрочный интервал в текстовом редакторе.
    def change_line_spacing(self):
        value = float(self.size_interval.currentText())
        cursor = self.text_edit.textCursor()
        cursor.select(QTextCursor.Document)

        # Получаем формат блока текста
        block_format = QTextBlockFormat()
        block_format.setLineHeight(value*10, QTextBlockFormat.LineHeightTypes.FixedHeight)  # установка фиксированного
        # межстрочного интервала

        # Применяем формат к выделенному тексту
        cursor.mergeBlockFormat(block_format)

        # Обновляем текст для применения нового межстрочного интервала
        self.text_edit.setTextCursor(cursor)
    def update_indent(self):
        sender = self.sender()
        if sender == self.increase_indentation:
            self.indent_value += 1
        elif self.indent_value > 0:
            self.indent_value -= 1
        block_format = QTextBlockFormat()
        block_format.setIndent(self.indent_value)
        cursor = self.text_edit.textCursor()
        cursor.select(QTextCursor.Document)
        cursor.mergeBlockFormat(block_format)
        self.text_edit.setTextCursor(cursor)
    def update_font(self, font=None):
        if font is None:
            font = self.font.currentFont()
        self.apply_font(font)

    def update_font_size(self):
        size = int(self.font_size.currentText())
        self.apply_font_size(size)

    def apply_font(self, font):
        current_font = self.text_edit.currentFont()
        new_font = QtGui.QFont(font.family(), current_font.pointSize())
        self.text_edit.setCurrentFont(new_font)

    def apply_font_size(self, size):
        current_font = self.text_edit.currentFont()
        new_font = QtGui.QFont(current_font.family(), size)
        self.text_edit.setCurrentFont(new_font)

    def toggle_bold(self):
        if self.bold_active:
            self.bold.setStyleSheet('background-color: none')
            self.bold_active = False
            self.apply_font_bold(False)
        else:
            self.bold.setStyleSheet('background-color: lightblue')
            self.bold_active = True
            self.apply_font_bold(True)

    def toggle_italic(self):
        if self.italic_active:
            self.italic.setStyleSheet('background-color: none')
            self.italic_active = False
            self.apply_font_italic(False)
        else:
            self.italic.setStyleSheet('background-color: lightblue')
            self.italic_active = True
            self.apply_font_italic(True)

    def toggle_underlined(self):
        if self.underlined_active:
            self.underlined.setStyleSheet('background-color: none')
            self.underlined_active = False
            self.apply_font_underlined(False)
        else:
            self.underlined.setStyleSheet('background-color: lightblue')
            self.underlined_active = True
            self.apply_font_underlined(True)

    def apply_font_bold(self, enabled):
        current_font = self.text_edit.currentFont()
        new_font = current_font
        new_font.setBold(enabled)
        self.text_edit.setCurrentFont(new_font)

    def apply_font_italic(self, enabled):
        current_font = self.text_edit.currentFont()
        new_font = current_font
        new_font.setItalic(enabled)
        self.text_edit.setCurrentFont(new_font)

    def apply_font_underlined(self, enabled):
        current_font = self.text_edit.currentFont()
        new_font = current_font
        new_font.setUnderline(enabled)
        self.text_edit.setCurrentFont(new_font)

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

        self.new_style_window = NewStyleWindow()
        self.new_style.clicked.connect(self.open_new_style_window)

    def open_new_style_window(self):
        self.new_style_window.show()

class NewStyleWindow(QtWidgets.QWidget, Ui_QtNewStyleWindow):
    def __init__(self):
        super().__init__()
        self.setupUi(self)

if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    main_window = MainWindow()
    main_window.show()
    sys.exit(app.exec_())


