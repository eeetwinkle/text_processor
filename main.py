import sys
from PyQt5 import QtWidgets, QtGui, QtCore
from QtMainWindow import Ui_color
from QtSearchWindow import Ui_QtSearchWindow
from QtReplaceWindow import Ui_QtReplaceWindow
from QtStyles import Ui_Form
from QtNewStyle import Ui_QtNewStyleWindow
from PyQt5.QtGui import QTextCursor, QTextBlockFormat
from PyQt5.QtWidgets import QColorDialog


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
        self.text_color.clicked.connect(self.change_text_color)

        self.bold_active = False
        self.italic_active = False
        self.underlined_active = False

        self.font.currentFontChanged.connect(self.update_font)
        self.font_size.currentIndexChanged.connect(self.update_font_size)

        self.bold.clicked.connect(self.toggle_bold)
        self.italic.clicked.connect(self.toggle_italic)
        self.underlined.clicked.connect(self.toggle_underlined)

        self.update_font()
        self.update_font_size()

        self.indent_value = 0
        self.reduce_indentation.clicked.connect(self.update_indent)
        self.increase_indentation.clicked.connect(self.update_indent)

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
        cursor = self.text_edit.textCursor()
        if cursor.hasSelection():
            format = cursor.charFormat()
            format.setFontFamily(font.family())
            cursor.setCharFormat(format)
        else:
            current_format = self.text_edit.currentCharFormat()
            current_format.setFontFamily(font.family())
            self.text_edit.setCurrentCharFormat(current_format)
        self.update_current_format()

    def apply_font_size(self, size):
        cursor = self.text_edit.textCursor()
        if cursor.hasSelection():
            format = cursor.charFormat()
            format.setFontPointSize(size)
            cursor.setCharFormat(format)
        else:
            current_format = self.text_edit.currentCharFormat()
            current_format.setFontPointSize(size)
            self.text_edit.setCurrentCharFormat(current_format)
        self.update_current_format()

    def toggle_bold(self):
        self.bold_active = not self.bold_active
        self.bold.setStyleSheet('background-color: lightblue' if self.bold_active else 'background-color: none')
        self.apply_font_bold(self.bold_active)

    def toggle_italic(self):
        self.italic_active = not self.italic_active
        self.italic.setStyleSheet('background-color: lightblue' if self.italic_active else 'background-color: none')
        self.apply_font_italic(self.italic_active)

    def toggle_underlined(self):
        self.underlined_active = not self.underlined_active
        self.underlined.setStyleSheet(
            'background-color: lightblue' if self.underlined_active else 'background-color: none')
        self.apply_font_underlined(self.underlined_active)
    def apply_font_bold(self, enabled):
        cursor = self.text_edit.textCursor()
        if cursor.hasSelection():
            format = cursor.charFormat()
            format.setFontWeight(QtGui.QFont.Bold if enabled else QtGui.QFont.Normal)
            cursor.setCharFormat(format)
        else:
            current_format = self.text_edit.currentCharFormat()
            current_format.setFontWeight(QtGui.QFont.Bold if enabled else QtGui.QFont.Normal)
            self.text_edit.setCurrentCharFormat(current_format)

    def apply_font_italic(self, enabled):
        cursor = self.text_edit.textCursor()
        if cursor.hasSelection():
            format = cursor.charFormat()
            format.setFontItalic(enabled)
            cursor.setCharFormat(format)
        else:
            current_format = self.text_edit.currentCharFormat()
            current_format.setFontItalic(enabled)
            self.text_edit.setCurrentCharFormat(current_format)

    def apply_font_underlined(self, enabled):
        cursor = self.text_edit.textCursor()
        if cursor.hasSelection():
            format = cursor.charFormat()
            format.setFontUnderline(enabled)
            cursor.setCharFormat(format)
        else:
            current_format = self.text_edit.currentCharFormat()
            current_format.setFontUnderline(enabled)
            self.text_edit.setCurrentCharFormat(current_format)

    def update_current_format(self):
        format = self.text_edit.currentCharFormat()
        format.setFontWeight(QtGui.QFont.Bold if self.bold_active else QtGui.QFont.Normal)
        format.setFontItalic(self.italic_active)
        format.setFontUnderline(self.underlined_active)
        self.text_edit.setCurrentCharFormat(format)

    def change_text_color(self):
        color = QColorDialog.getColor()
        if color.isValid():
            cursor = self.text_edit.textCursor()
            if cursor.hasSelection():
                format = cursor.charFormat()
                format.setForeground(color)
                cursor.setCharFormat(format)
            else:
                current_format = self.text_edit.currentCharFormat()
                current_format.setForeground(color)
                self.text_edit.setCurrentCharFormat(current_format)

            self.text_color.setStyleSheet(
                f'background-color: {color.name()}' if color != QtGui.QColor('black') else 'background-color: none')

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
