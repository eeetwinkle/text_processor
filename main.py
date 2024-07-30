import sys
import re
import sqlite3
from PyQt5 import QtWidgets, QtGui
from PyQt5.QtGui import QTextCursor, QTextBlockFormat, QTextImageFormat, QPixmap, QTextDocument, QTextFrameFormat
from PyQt5.QtWidgets import QColorDialog, QFileDialog, QMessageBox, QInputDialog
from PyQt5.QtPrintSupport import QPrinter
from QtMainWindow import Ui_color
from QtSearchWindow import Ui_QtSearchWindow
from QtReplaceWindow import Ui_QtReplaceWindow
from QtStyles import Ui_Form
from QtNewStyle import Ui_QtNewStyleWindow


class MainWindow(QtWidgets.QMainWindow, Ui_color):
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.search_window = SearchWindow(self.text_edit)
        self.replace_window = ReplaceWindow(self.text_edit)
        self.style_window = StyleWindow()
        self.search.clicked.connect(self.open_search_window)
        self.replace.clicked.connect(self.open_replace_window)
        self.style.clicked.connect(self.open_style_window)
        self.text_color.clicked.connect(self.change_text_color)
        self.save.clicked.connect(self.save_as_pdf)

        self.bold_active = False
        self.italic_active = False
        self.underlined_active = False

        self.font.currentFontChanged.connect(self.update_font)
        self.font_size.currentIndexChanged.connect(self.update_font_size)
        self.size_interval.currentIndexChanged.connect(self.update_line_spacing)
        self.pages.valueChanged.connect(self.change_page)

        self.bold.clicked.connect(self.toggle_bold)
        self.italic.clicked.connect(self.toggle_italic)
        self.underlined.clicked.connect(self.toggle_underlined)

        self.update_font()
        self.update_font_size()

        self.indent_value = 0
        self.reduce_indentation.clicked.connect(self.update_indent)
        self.increase_indentation.clicked.connect(self.update_indent)

        self.paste.clicked.connect(self.insert_image)

        self.page_contents = {}
        self.current_page = 1
        self.pages.setMinimum(1)
        self.pages.setValue(1)
        self.load_page_content()

        self.set_page_margins()

    def set_page_margins(self):
        page_format = QTextFrameFormat()
        page_format.setLeftMargin(50)
        page_format.setRightMargin(50)
        page_format.setTopMargin(50)
        page_format.setBottomMargin(50)
        self.text_edit.document().rootFrame().setFrameFormat(page_format)

    def update_line_spacing(self):
        value = self.size_interval.currentText()
        try:
            spacing = float(value)
        except ValueError:
            return

        cursor = self.text_edit.textCursor()
        block_format = cursor.blockFormat()
        block_format.setLineHeight(spacing * 100, QtGui.QTextBlockFormat.ProportionalHeight)
        cursor.setBlockFormat(block_format)
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
        format = QtGui.QTextCharFormat()
        format.setFontFamily(font.family())
        self.merge_format_on_word_or_selection(format)

    def apply_font_size(self, size):
        format = QtGui.QTextCharFormat()
        format.setFontPointSize(size)
        self.merge_format_on_word_or_selection(format)

    def toggle_bold(self):
        self.bold_active = not self.bold_active
        self.bold.setStyleSheet('background-color: lightblue' if self.bold_active else 'background-color: none')
        format = QtGui.QTextCharFormat()
        format.setFontWeight(QtGui.QFont.Bold if self.bold_active else QtGui.QFont.Normal)
        self.merge_format_on_word_or_selection(format)

    def toggle_italic(self):
        self.italic_active = not self.italic_active
        self.italic.setStyleSheet('background-color: lightblue' if self.italic_active else 'background-color: none')
        format = QtGui.QTextCharFormat()
        format.setFontItalic(self.italic_active)
        self.merge_format_on_word_or_selection(format)

    def toggle_underlined(self):
        self.underlined_active = not self.underlined_active
        self.underlined.setStyleSheet(
            'background-color: lightblue' if self.underlined_active else 'background-color: none')
        format = QtGui.QTextCharFormat()
        format.setFontUnderline(self.underlined_active)
        self.merge_format_on_word_or_selection(format)

    def change_text_color(self):
        color = QColorDialog.getColor()
        if color.isValid():
            format = QtGui.QTextCharFormat()
            format.setForeground(color)
            self.merge_format_on_word_or_selection(format)
            self.text_color.setStyleSheet(
                f'background-color: {color.name()}' if color != QtGui.QColor('black') else 'background-color: none')

    def merge_format_on_word_or_selection(self, format):
        cursor = self.text_edit.textCursor()
        if not cursor.hasSelection():
            cursor.select(QTextCursor.WordUnderCursor)
        cursor.mergeCharFormat(format)
        self.text_edit.mergeCurrentCharFormat(format)

    def update_current_format(self):
        format = self.text_edit.currentCharFormat()
        format.setFontWeight(QtGui.QFont.Bold if self.bold_active else QtGui.QFont.Normal)
        format.setFontItalic(self.italic_active)
        format.setFontUnderline(self.underlined_active)
        self.text_edit.setCurrentCharFormat(format)

    def save_as_pdf(self):
        self.page_contents[self.current_page] = self.text_edit.toHtml()

        file_path, _ = QFileDialog.getSaveFileName(self, "Save File", "", "PDF Files (*.pdf)")
        if file_path:
            try:
                printer = QPrinter(QPrinter.HighResolution)
                printer.setOutputFormat(QPrinter.PdfFormat)
                printer.setOutputFileName(file_path)

                final_document = QTextDocument()

                full_html = "<html><body>"
                for page in sorted(self.page_contents.keys()):
                    text = self.page_contents.get(page, "")
                    if page != min(self.page_contents.keys()):
                        full_html += "<div style='page-break-before:always;'></div>"
                    full_html += f"<div>{text}</div>"

                full_html += "</body></html>"

                final_document.setHtml(full_html)
                final_document.print_(printer)
                QMessageBox.information(self, "Сохранение завершено", f"Документ сохранен по пути {file_path}")

            except Exception as e:
                QMessageBox.critical(self, "Ошибка сохранения", f"Произошла ошибка при сохранении PDF: {str(e)}")

    def change_page(self):
        self.page_contents[self.current_page] = self.text_edit.toHtml()

        self.current_page = self.pages.value()
        self.load_page_content()

    def load_page_content(self):
        text = self.page_contents.get(self.current_page, "")
        self.text_edit.setHtml(text)

    def insert_image(self):
        options = QFileDialog.Options()
        file_name, _ = QFileDialog.getOpenFileName(self, "Выберите изображение", "",
                                                   "Images (*.png *.xpm *.jpg *.jpeg);;All Files (*)", options=options)
        if file_name:
            try:
                cursor = self.text_edit.textCursor()
                image_format = QTextImageFormat()
                image_format.setName(file_name)

                # Получаем исходные размеры изображения
                pixmap = QPixmap(file_name)
                if pixmap.isNull():
                    raise ValueError("Изображение не может быть загружено.")

                # Запрашиваем новые размеры у пользователя с предложением использовать исходные
                default_width = pixmap.width()
                default_height = pixmap.height()
                width, ok = QInputDialog.getInt(self, "Ширина изображения", "Введите ширину:", default_width, 1, 3000)
                if ok:
                    height, ok = QInputDialog.getInt(self, "Высота изображения", "Введите высоту:", default_height, 1,
                                                     3000)
                    if ok:
                        image_format.setWidth(width)
                        image_format.setHeight(height)
                        cursor.insertImage(image_format)
            except Exception as e:
                QMessageBox.critical(self, "Ошибка", f"Не удалось вставить изображение: {str(e)}")

    def open_search_window(self):
        self.search_window.show()

    def open_replace_window(self):
        self.replace_window.show()

    def open_style_window(self):
        self.style_window.show()


class SearchWindow(QtWidgets.QWidget, Ui_QtSearchWindow):
    def __init__(self, text_edit):
        super().__init__()
        self.text_edit = text_edit
        self.setupUi(self)
        self.pushButton_search.clicked.connect(self.perform_search)
        self.pushButton_search_2.clicked.connect(self.navigate_to_next)
        self.pushButton_search_3.clicked.connect(self.navigate_to_previous)

    # Метод, выполняющий поиск по тексту
    def perform_search(self):
        search_text = self.lineEdit_search.text()
        if self.checkBox_register.isChecked():
            flags = 0
        else:
            flags = re.IGNORECASE  # Учитываем регистр иначе

        whole_word = self.checkBox_entirely.isChecked()
        pattern = search_text
        if whole_word:
            pattern = r'\b' + re.escape(search_text) + r'\b'

        text = self.text_edit.toPlainText()
        self.found_positions = [m.start() for m in re.finditer(pattern, text, flags)]
        count = len(self.found_positions)

        if count == 0:
            self.show_message("Не найдено")
            self.current_index = -1  # Сбрасываем индекс
            self.clear_highlight()
        else:
            self.show_message(f"Найдено: {count} вхождений")
            self.current_index = 0  # Сбрасываем индекс для первого вхождения
            self.highlight_current_word()

    # Метод для выделения текущего найденного слова
    def highlight_current_word(self):
        self.clear_highlight()  # Сначала снимаем выделение

        if self.current_index >= 0 and self.current_index < len(self.found_positions):
            cursor = self.text_edit.textCursor()
            pos = self.found_positions[self.current_index]
            cursor.setPosition(pos)
            cursor.movePosition(cursor.Right, cursor.KeepAnchor, len(self.lineEdit_search.text()))
            self.text_edit.setTextCursor(cursor)
            self.text_edit.setFocus()

    # Метод для снятия выделения
    def clear_highlight(self):
        cursor = self.text_edit.textCursor()
        cursor.clearSelection()
        self.text_edit.setTextCursor(cursor)

    # Метод для отображения сообщения в диалоговом окне
    def show_message(self, message):
        msg_box = QMessageBox()
        msg_box.setText(message)
        msg_box.exec_()

    # Навигация к следующему найденному слову
    def navigate_to_next(self):
        if not self.found_positions:
            return
        self.current_index = (self.current_index + 1) % len(self.found_positions)
        self.highlight_current_word()

    # Навигация к предыдущему найденному слову
    def navigate_to_previous(self):
        if not self.found_positions:
            return
        self.current_index = (self.current_index - 1) % len(self.found_positions)
        self.highlight_current_word()


class ReplaceWindow(QtWidgets.QWidget, Ui_QtReplaceWindow):
    def __init__(self, text_edit):
        super().__init__()
        self.text_edit = text_edit
        self.setupUi(self)
        self.pushButton_replace.clicked.connect(self.replace_all)

    # Метод, выполняющий замену всех найденных слов
    def replace_all(self):
        word_to_replace = self.lineEdit_search2.text()
        replacement_word = self.lineEdit_replace.text()

        if not word_to_replace:
            self.show_message("Пожалуйста, введите слово для замены.")
            return

        if self.checkBox_register.isChecked():
            flags = 0
        else:
            flags = re.IGNORECASE  # Учитываем регистр иначе

        whole_word = self.checkBox_entirely.isChecked()
        pattern = word_to_replace
        if whole_word:
            pattern = r'\b' + re.escape(word_to_replace) + r'\b'

        text = self.text_edit.toPlainText()
        new_text = re.sub(pattern, replacement_word, text, flags=flags)
        self.text_edit.setPlainText(new_text)

        self.show_message(f"Все вхождения '{word_to_replace}' заменены на '{replacement_word}'.")

    # Метод для отображения сообщения в диалоговом окне
    def show_message(self, message):
        msg_box = QMessageBox()
        msg_box.setText(message)
        msg_box.exec_()


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
        self.bold_active = False
        self.italic_active = False
        self.underlined_active = False
        self.current_text_color = QtGui.QColor('black')  # Изначальный цвет текста
        self.text_color.clicked.connect(self.change_text_color)
        self.font.currentFontChanged.connect(self.update_font)
        self.font_size.currentIndexChanged.connect(self.update_font_size)
        self.line_spacing.currentIndexChanged.connect(self.update_line_spacing)

        self.bold.clicked.connect(self.toggle_bold)
        self.italic.clicked.connect(self.toggle_italic)
        self.underlined.clicked.connect(self.toggle_underlined)

        self.save.clicked.connect(self.save_style)

        self.update_font()
        self.update_font_size()

        self.indent_value = 0
        self.reduce_indentation.clicked.connect(self.update_indent)
        self.increase_indentation.clicked.connect(self.update_indent)

    # Новый метод для сохранения стиля
    def save_style(self):
        style_name = self.style_name.text()
        current_font = self.font.currentFont().family()
        font_size = int(self.font_size.currentText())
        text_color = self.current_text_color.name()
        line_spacing = float(self.line_spacing.currentText())
        is_bold = self.bold_active
        is_italic = self.italic_active
        is_underlined = self.underlined_active

        self.add_row(style_name, current_font, font_size, is_bold, is_italic, is_underlined, line_spacing, text_color)

    def update_line_spacing(self):
        value = self.line_spacing.currentText()
        try:
            spacing = float(value)
        except ValueError:
            return

        cursor = self.text_edit.textCursor()
        block_format = cursor.blockFormat()
        block_format.setLineHeight(spacing * 100, QtGui.QTextBlockFormat.ProportionalHeight)
        cursor.setBlockFormat(block_format)
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
        format = QtGui.QTextCharFormat()
        format.setFontFamily(font.family())
        self.merge_format_on_word_or_selection(format)

    def apply_font_size(self, size):
        format = QtGui.QTextCharFormat()
        format.setFontPointSize(size)
        self.merge_format_on_word_or_selection(format)

    def toggle_bold(self):
        self.bold_active = not self.bold_active
        self.bold.setStyleSheet('background-color: lightblue' if self.bold_active else 'background-color: none')
        format = QtGui.QTextCharFormat()
        format.setFontWeight(QtGui.QFont.Bold if self.bold_active else QtGui.QFont.Normal)
        self.merge_format_on_word_or_selection(format)

    def toggle_italic(self):
        self.italic_active = not self.italic_active
        self.italic.setStyleSheet('background-color: lightblue' if self.italic_active else 'background-color: none')
        format = QtGui.QTextCharFormat()
        format.setFontItalic(self.italic_active)
        self.merge_format_on_word_or_selection(format)

    def toggle_underlined(self):
        self.underlined_active = not self.underlined_active
        self.underlined.setStyleSheet(
            'background-color: lightblue' if self.underlined_active else 'background-color: none')
        format = QtGui.QTextCharFormat()
        format.setFontUnderline(self.underlined_active)
        self.merge_format_on_word_or_selection(format)

    def change_text_color(self):
        color = QColorDialog.getColor()
        if color.isValid():
            self.current_text_color = color  # Обновляем текущий цвет текста
            format = QtGui.QTextCharFormat()
            format.setForeground(color)
            self.merge_format_on_word_or_selection(format)
            self.text_color.setStyleSheet(
                f'background-color: {color.name()}' if color != QtGui.QColor('black') else 'background-color: none')

    def get_current_text_color(self):
        return self.current_text_color

    def merge_format_on_word_or_selection(self, format):
        cursor = self.text_edit.textCursor()
        if not cursor.hasSelection():
            cursor.select(QTextCursor.WordUnderCursor)
        cursor.mergeCharFormat(format)
        self.text_edit.mergeCurrentCharFormat(format)

    def show_message(self, message):
        msg_box = QMessageBox()
        msg_box.setText(message)
        msg_box.exec_()

    def add_row(self, name, shrift, pt, bold, italic, underlined, interval, color):
        print(
            f"Style Name: {name}, Font: {shrift}, Size: {pt}, Color: {color}, Spacing: {interval}, Bold: {bold}, Italic: {italic}, Underlined: {underlined}")

        self.conn = sqlite3.connect("text_processor.db")
        if name != '':
            try:
                cur = self.conn.cursor()
                a = f"""INSERT INTO styles(name, shrift, pt, bold, italic, underlined, interval, color) 
                VALUES("{name}", "{shrift}", {pt}, "{bold}", "{italic}", "{underlined}", {interval}, "{color}" )"""
                cur.execute(a)
                self.conn.commit()
                cur.close()

                self.show_message("Успешное добавление стиля")

            except Exception as e:
                self.show_message("не добавлено")
                print(e)
        else:
            self.show_message("Придумайте название стиля")


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    main_window = MainWindow()
    main_window.show()
    sys.exit(app.exec_())