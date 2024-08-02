import sys
import re
import sqlite3
import webbrowser

from PyQt5 import QtWidgets, QtGui, QtCore
from PyQt5.QtCore import QUrl
from PyQt5.QtGui import QTextCursor, QTextBlockFormat, QTextImageFormat, QPixmap, QTextDocument, QTextFrameFormat, QFont
from PyQt5.QtWidgets import QColorDialog, QFileDialog, QMessageBox, QInputDialog, QWidget, QVBoxLayout, QRadioButton
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
        self.setWindowTitle("Текстовый редактор")
        self.search_window = SearchWindow(self.text_edit)
        self.replace_window = ReplaceWindow(self.text_edit)
        self.style_window = StyleWindow()

        self.search.clicked.connect(self.open_search_window)
        self.replace.clicked.connect(self.open_replace_window)
        self.style.clicked.connect(self.open_style_window)
        self.text_color.clicked.connect(self.change_text_color)
        self.save.clicked.connect(self.save_document)
        self.upload.clicked.connect(self.open_html_file)
        self.bold.clicked.connect(self.toggle_bold)
        self.italic.clicked.connect(self.toggle_italic)
        self.underlined.clicked.connect(self.toggle_underlined)
        self.font.currentFontChanged.connect(self.update_font)
        self.font_size.currentIndexChanged.connect(self.update_font_size)
        self.size_interval.currentIndexChanged.connect(self.update_line_spacing)
        self.pages.valueChanged.connect(self.change_page)
        self.reduce_indentation.clicked.connect(self.update_indent)
        self.increase_indentation.clicked.connect(self.update_indent)
        self.paste.clicked.connect(self.insert_image)
        self.link.clicked.connect(self.add_link)
        self.text_edit.selectionChanged.connect(self.update_open_link)
        self.text_edit.textChanged.connect(self.on_text_changed)
        self.style_window.style_selected.connect(self.apply_style)

        self.bold_active = False
        self.italic_active = False
        self.underlined_active = False
        self.current_text_color = QtGui.QColor('black')
        self.page_contents = {}
        self.current_page = 1
        self.pages.setMinimum(1)
        self.pages.setValue(1)
        self.ignore_modifications = False
        self.indent_value = 0
        self.previous_text = self.text_edit.toPlainText()

        self.update_font()
        self.update_font_size()
        self.load_page_content()
        self.set_page_margins()

    def open_search_window(self):
        self.search_window.show()

    def open_replace_window(self):
        self.replace_window.show()

    def open_style_window(self):
        self.style_window.show()

    def save_document(self):
        warning_message = (
            "Если вы хотите в дальнейшем редактировать файл, сохраните его в формате HTML.\n"
            "Если вы хотите просматривать готовый документ, сохраните его в формате PDF."
        )
        reply = QMessageBox.warning(
            self,
            "Предупреждение",
            warning_message,
            QMessageBox.Ok
        )

        if reply == QMessageBox.Cancel:
            return

        self.page_contents[self.current_page] = self.text_edit.toHtml()

        options = QFileDialog.Options()
        file_path, _ = QFileDialog.getSaveFileName(self, "Save File", "", "HTML Files (*.html);;PDF Files (*.pdf)",
                                                   options=options)

        if file_path:
            if file_path.endswith('.pdf'):
                self.save_as_pdf(file_path)
            elif file_path.endswith('.html'):
                self.save_as_html(file_path)

    def save_as_pdf(self, file_path):
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

            self.text_edit.document().setModified(False)

            QMessageBox.information(self, "Сохранение завершено", f"Документ сохранен по пути {file_path}")

        except Exception as e:
            QMessageBox.critical(self, "Ошибка сохранения", f"Произошла ошибка при сохранении PDF: {str(e)}")

    def save_as_html(self, file_path):
        try:
            full_html = "<html><body>"
            for page in sorted(self.page_contents.keys()):
                text = self.page_contents.get(page, "")
                if page != min(self.page_contents.keys()):
                    full_html += "<div style='page-break-before:always;'></div>"
                full_html += f"<div>{text}</div>"
            full_html += "</body></html>"

            with open(file_path, 'w', encoding='utf-8') as file:
                file.write(full_html)

            self.text_edit.document().setModified(False)

            QMessageBox.information(self, "Сохранение завершено", f"Документ сохранен по пути {file_path}")

        except Exception as e:
            QMessageBox.critical(self, "Ошибка сохранения", f"Произошла ошибка при сохранении HTML: {str(e)}")

    def open_html_file(self):
        if not self.text_edit.document().isEmpty() and self.text_edit.document().isModified():
            unsaved_warning_message = (
                "У вас есть несохраненные данные. Они будут утеряны при открытии нового файла. Продолжить?")
            message_box = QMessageBox()
            message_box.setIcon(QMessageBox.Warning)
            message_box.setWindowTitle("Предупреждение")
            message_box.setText(unsaved_warning_message)
            continue_button = message_box.addButton("Продолжить", QMessageBox.AcceptRole)
            cancel_button = message_box.addButton("Отменить", QMessageBox.RejectRole)
            message_box.setDefaultButton(cancel_button)

            message_box.exec_()

            if message_box.clickedButton() == cancel_button:
                return

        self.page_contents[self.current_page] = self.text_edit.toHtml()

        self.current_page = 1
        self.pages.setValue(1)

        options = QFileDialog.Options()
        file_path, _ = QFileDialog.getOpenFileName(self, "Открыть файл", "", "HTML Files (*.html);;All Files (*)",
                                                   options=options)

        if file_path:
            try:
                with open(file_path, 'r', encoding='utf-8') as file:
                    html_content = file.read()

                self.page_contents.clear()
                self.text_edit.clear()

                pages = html_content.split("<div style='page-break-before:always;'></div>")
                self.page_contents = {i + 1: page for i, page in enumerate(pages)}

                self.current_page = 1
                self.pages.setMinimum(1)
                self.pages.setMaximum(len(self.page_contents))
                self.pages.setValue(1)
                self.ignore_modifications = True
                self.load_page_content()
                self.ignore_modifications = False

                self.text_edit.document().setModified(False)

                QMessageBox.information(self, "Загрузка завершена", f"Документ успешно загружен из {file_path}")

            except Exception as e:
                QMessageBox.critical(self, "Ошибка загрузки", f"Произошла ошибка при загрузке HTML: {str(e)}")

    def on_text_changed(self):
        text = self.text_edit.toPlainText()

        self.text_edit.textChanged.disconnect(self.on_text_changed)

        if not text or text != self.previous_text:
            self.update_font()
            self.update_line_spacing()
            self.update_font_size()

            self.bold_active = not self.bold_active
            self.italic_active = not self.italic_active
            self.underlined_active = not self.underlined_active

            self.toggle_bold()
            self.toggle_italic()
            self.toggle_underlined()

            self.current_text_color = self.current_text_color
            format = QtGui.QTextCharFormat()
            format.setForeground(self.current_text_color)
            self.merge_format_on_word_or_selection(format)
            self.previous_text = text
        self.text_edit.textChanged.connect(self.on_text_changed)

    def apply_style(self, style_name):
        conn = sqlite3.connect('text_processor.db')
        cur = conn.cursor()

        cur.execute("SELECT * FROM styles WHERE name = ?", (style_name,))
        style = cur.fetchone()

        if style:
            font_family = style[1]
            font_size = style[2]
            is_bold = style[3]
            if is_bold == "True":
                is_bold = True
            else:
                is_bold = False
            is_italic = style[4]
            if is_italic == "True":
                is_italic = True
            else:
                is_italic = False
            is_underline = style[5]
            if is_underline == "True":
                is_underline = True
            else:
                is_underline = False
            line_spacing = style[6]
            font_color = style[7]

            format = QtGui.QTextCharFormat()
            format.setForeground(QtGui.QColor(font_color))
            self.merge_format_on_word_or_selection(format)
            self.current_text_color = QtGui.QColor(font_color)
            self.text_color.setStyleSheet(f'background-color: {font_color}' if font_color != QtGui.QColor('black')
                                          else 'background-color: none')

            self.size_interval.setCurrentText(line_spacing)
            font = QFont(font_family)
            self.font.setCurrentFont(font)

            self.font_size.setCurrentText(font_size)

            self.update_font()
            self.update_line_spacing()
            self.update_font_size()

            self.bold_active = not is_bold
            self.italic_active = not is_italic
            self.underlined_active = not is_underline

            self.toggle_bold()
            self.toggle_italic()
            self.toggle_underlined()
        conn.close()

    def change_text_color(self):
        color = QColorDialog.getColor()
        if color.isValid():
            self.current_text_color = color
            format = QtGui.QTextCharFormat()
            format.setForeground(color)
            self.merge_format_on_word_or_selection(format)
            self.text_color.setStyleSheet(f'background-color: {color.name()}' if color != QtGui.QColor('black')
                                          else 'background-color: none')

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

    def insert_image(self):
        options = QFileDialog.Options()
        file_name, _ = QFileDialog.getOpenFileName(self, "Выберите изображение", "",
                                                   "Images (*.png *.xpm *.jpg *.jpeg);;All Files (*)", options=options)
        if file_name:
            try:
                cursor = self.text_edit.textCursor()
                image_format = QTextImageFormat()
                image_format.setName(file_name)

                pixmap = QPixmap(file_name)
                if pixmap.isNull():
                    raise ValueError("Изображение не может быть загружено.")

                default_width = pixmap.width()
                default_height = pixmap.height()
                width, ok = QInputDialog.getInt(self, "Ширина изображения", "Введите ширину:", default_width, 1, 3000)
                if ok:
                    height, ok = QInputDialog.getInt(self, "Высота изображения", "Введите высоту:",
                                                     default_height, 1, 3000)
                    if ok:
                        image_format.setWidth(width)
                        image_format.setHeight(height)
                        cursor.insertImage(image_format)
                        self.update_font()
                        self.update_line_spacing()
                        self.update_font_size()

                        self.bold_active = not self.bold_active
                        self.italic_active = not self.italic_active
                        self.underlined_active = not self.underlined_active

                        self.toggle_bold()
                        self.toggle_italic()
                        self.toggle_underlined()

                        self.current_text_color = self.current_text_color
                        format = QtGui.QTextCharFormat()
                        format.setForeground(self.current_text_color)
                        self.merge_format_on_word_or_selection(format)
            except Exception as e:
                QMessageBox.critical(self, "Ошибка", f"Не удалось вставить изображение: {str(e)}")

    def add_link(self):
        link_text, ok1 = QInputDialog.getText(self, 'Текст ссылки', 'Введите текст для ссылки:')
        if ok1 and link_text:
            url, ok2 = QInputDialog.getText(self, 'URL ссылки',
                                            'Введите URL для ссылки (например, http://example.com):')
            if ok2 and url:
                cursor = self.text_edit.textCursor()

                cursor.insertHtml(f'<a href="{url}">{link_text}</a> ')

                self.text_edit.setTextCursor(cursor)

                self.update_font()
                self.update_line_spacing()
                self.update_font_size()

                self.bold_active = not self.bold_active
                self.italic_active = not self.italic_active
                self.underlined_active = not self.underlined_active

                self.toggle_bold()
                self.toggle_italic()
                self.toggle_underlined()

                self.current_text_color = self.current_text_color
                format = QtGui.QTextCharFormat()
                format.setForeground(self.current_text_color)
                self.merge_format_on_word_or_selection(format)

    def update_open_link(self):
        cursor = self.text_edit.textCursor()
        selected_text = cursor.selectedText()
        if self.is_link_selected(cursor):
            self.open_link()

    def open_link(self):
        cursor = self.text_edit.textCursor()
        if self.is_link_selected(cursor):
            link_format = cursor.charFormat()
            url = link_format.anchorHref()
            if url:
                self.show_link_dialog(url)

    def show_link_dialog(self, url):
        reply = QMessageBox.question(self, 'Переход по ссылке', f'Хотите перейти по ссылке: {url}?',
                                     QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        if reply == QMessageBox.Yes:
            webbrowser.open(QUrl(url).toString())

    def is_link_selected(self, cursor):
        cursor.select(QTextCursor.WordUnderCursor)
        link_format = cursor.charFormat()
        return link_format.isAnchor()

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
        self.underlined.setStyleSheet('background-color: lightblue' if self.underlined_active
                                      else 'background-color: none')
        format = QtGui.QTextCharFormat()
        format.setFontUnderline(self.underlined_active)
        self.merge_format_on_word_or_selection(format)

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

    def set_page_margins(self):
        page_format = QTextFrameFormat()
        page_format.setLeftMargin(50)
        page_format.setRightMargin(50)
        page_format.setTopMargin(50)
        page_format.setBottomMargin(50)
        self.text_edit.document().rootFrame().setFrameFormat(page_format)

    def change_page(self):
        self.page_contents[self.current_page] = self.text_edit.toHtml()

        self.current_page = self.pages.value()

        self.ignore_modifications = True
        self.load_page_content()
        self.ignore_modifications = False

    def load_page_content(self):
        text = self.page_contents.get(self.current_page, "")
        self.text_edit.setHtml(text)
        self.set_page_margins()
        self.text_edit.document().setModified(False)

    def closeEvent(self, event):
        if self.text_edit.document().isModified():
            unsaved_warning_message = ("У вас есть несохраненные данные. Они будут утеряны при закрытии программы. "
                                       "Хотите сохранить изменения?")
            message_box = QMessageBox()
            message_box.setIcon(QMessageBox.Warning)
            message_box.setWindowTitle("Предупреждение")
            message_box.setText(unsaved_warning_message)
            save_button = message_box.addButton("Сохранить", QMessageBox.AcceptRole)
            discard_button = message_box.addButton("Не сохранять", QMessageBox.DestructiveRole)
            message_box.setDefaultButton(save_button)

            message_box.exec_()

            if message_box.clickedButton() == save_button:
                self.save_document()
                event.accept()
            elif message_box.clickedButton() == discard_button:
                event.accept()
            else:
                event.ignore()
        else:
            event.accept()


class SearchWindow(QtWidgets.QWidget, Ui_QtSearchWindow):
    def __init__(self, text_edit):
        super().__init__()
        self.text_edit = text_edit
        self.setupUi(self)
        self.setWindowTitle("Поиск")
        self.pushButton_search.clicked.connect(self.perform_search)
        self.pushButton_search_2.clicked.connect(self.navigate_to_next)
        self.pushButton_search_3.clicked.connect(self.navigate_to_previous)
        self.found_positions = []
        self.current_index = -1

    def perform_search(self):
        search_text = self.lineEdit_search.text()
        flags = re.IGNORECASE if not self.checkBox_register.isChecked() else 0
        pattern = re.escape(search_text) if not self.checkBox_entirely.isChecked() else r'\b' + re.escape(search_text) + r'\b'

        text = self.text_edit.toPlainText()
        self.found_positions = [m.start() for m in re.finditer(pattern, text, flags)]
        count = len(self.found_positions)

        if count == 0:
            self.show_message("Не найдено")
            self.current_index = -1
            self.clear_highlight()
        else:
            self.show_message(f"Найдено: {count} вхождений")
            self.current_index = 0
            self.highlight_current_word()

    def highlight_current_word(self):
        self.clear_highlight()

        if self.current_index >= 0 and self.current_index < len(self.found_positions):
            cursor = self.text_edit.textCursor()
            pos = self.found_positions[self.current_index]
            cursor.setPosition(pos)
            cursor.movePosition(cursor.Right, cursor.KeepAnchor, len(self.lineEdit_search.text()))
            self.text_edit.setTextCursor(cursor)
            self.text_edit.setFocus()

    def clear_highlight(self):
        cursor = self.text_edit.textCursor()
        cursor.clearSelection()
        self.text_edit.setTextCursor(cursor)

    def show_message(self, message):
        msg_box = QMessageBox()
        msg_box.setText(message)
        msg_box.exec_()

    def navigate_to_next(self):
        if not self.found_positions:
            return
        self.current_index = (self.current_index + 1) % len(self.found_positions)
        self.highlight_current_word()

    def navigate_to_previous(self):
        if not self.found_positions:
            return
        self.current_index = (self.current_index - 1) % len(self.found_positions)
        self.highlight_current_word()

    def closeEvent(self, event):
        self.lineEdit_search.clear()
        self.checkBox_entirely.setChecked(False)
        self.checkBox_register.setChecked(False)
        event.accept()


class ReplaceWindow(QtWidgets.QWidget, Ui_QtReplaceWindow):
    def __init__(self, text_edit):
        super().__init__()
        self.text_edit = text_edit
        self.setupUi(self)
        self.setWindowTitle("Заменить")
        self.pushButton_replace.clicked.connect(self.replace_all)

    def replace_all(self):
        word_to_replace = self.lineEdit_search2.text()
        replacement_word = self.lineEdit_replace.text()

        if not word_to_replace:
            self.show_message("Пожалуйста, введите слово для замены.")
            return

        flags = re.IGNORECASE if not self.checkBox_register.isChecked() else 0
        pattern = re.escape(word_to_replace) if not self.checkBox_entirely.isChecked() else r'\b' + re.escape(word_to_replace) + r'\b'

        text = self.text_edit.toPlainText()
        new_text = re.sub(pattern, replacement_word, text, flags=flags)
        self.text_edit.setPlainText(new_text)

        main_window.set_page_margins()

        self.show_message(f"Все вхождения '{word_to_replace}' заменены на '{replacement_word}'.")
        self.close()

    def show_message(self, message):
        msg_box = QMessageBox()
        msg_box.setText(message)
        msg_box.exec_()

    def closeEvent(self, event):
        self.lineEdit_replace.clear()
        self.lineEdit_search2.clear()
        self.checkBox_entirely.setChecked(False)
        self.checkBox_register.setChecked(False)
        event.accept()


class StyleWindow(QtWidgets.QWidget, Ui_Form):
    style_selected = QtCore.pyqtSignal(str)

    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.setWindowTitle("Стили")

        self.new_style_window = NewStyleWindow()
        self.new_style.clicked.connect(self.open_new_style_window)

        self.conn = sqlite3.connect('text_processor.db')
        self.cur = self.conn.cursor()

        self.radio_container = QWidget()
        self.radio_layout = QVBoxLayout(self.radio_container)
        self.scrollArea.setWidget(self.radio_container)

        self.scrollArea.setWidgetResizable(True)
        self.save.clicked.connect(self.save_style)

    def save_style(self):
        selected_style = None
        for i in range(self.radio_layout.count()):
            radio_button = self.radio_layout.itemAt(i).widget()
            if radio_button and radio_button.isChecked():
                selected_style = radio_button.text()
                break

        if selected_style:
            self.style_selected.emit(selected_style)
            self.close()

    def showEvent(self, event):
        self.update_scroll_area()
        super().showEvent(event)

    def update_scroll_area(self):
        for i in reversed(range(self.radio_layout.count())):
            widget = self.radio_layout.itemAt(i).widget()
            if widget is not None:
                widget.deleteLater()

        self.cur.execute("SELECT name FROM styles")
        styles = self.cur.fetchall()

        for style in styles:
            radio_button = QRadioButton(style[0])
            self.radio_layout.addWidget(radio_button)

    def open_new_style_window(self):
        self.new_style_window.show()
        self.close()


class NewStyleWindow(QtWidgets.QWidget, Ui_QtNewStyleWindow):
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.setWindowTitle("Создать новый стиль")
        self.bold_active = False
        self.italic_active = False
        self.underlined_active = False
        self.current_text_color = QtGui.QColor('black')
        format = QtGui.QTextCharFormat()
        format.setForeground(self.current_text_color)
        self.merge_format_on_word_or_selection(format)
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
        self.esc.clicked.connect(self.closing)

        self.text_edit.textChanged.connect(self.on_text_changed)

    def on_text_changed(self):
        text = self.text_edit.toPlainText()

        self.text_edit.textChanged.disconnect(self.on_text_changed)

        if not text:
            self.update_font()
            self.update_line_spacing()
            self.update_font_size()

            self.bold_active = not self.bold_active
            self.italic_active = not self.italic_active
            self.underlined_active = not self.underlined_active

            self.toggle_bold()
            self.toggle_italic()
            self.toggle_underlined()

            self.current_text_color = self.current_text_color
            format = QtGui.QTextCharFormat()
            format.setForeground(self.current_text_color)
            self.merge_format_on_word_or_selection(format)

        self.text_edit.textChanged.connect(self.on_text_changed)

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
            self.current_text_color = color
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
        self.conn = sqlite3.connect("text_processor.db")
        if name != '':
            try:
                cur = self.conn.cursor()
                a = f"""INSERT INTO styles(name, shrift, pt, bold, italic, underlined, interval, color) 
                VALUES("{name}", "{shrift}", "{pt}", "{bold}", "{italic}", "{underlined}", "{interval}", "{color}" )"""
                cur.execute(a)
                self.conn.commit()
                cur.close()

                self.show_message("Успешное добавление стиля")

                self.closing()

            except Exception as e:
                self.show_message("не добавлено")
                print(e)
        else:
            self.show_message("Придумайте название стиля")

    def closing(self):
        self.text_edit.clear()
        self.style_name.clear()
        self.current_text_color = QtGui.QColor('black')
        format = QtGui.QTextCharFormat()
        format.setForeground(self.current_text_color)
        self.text_color.setStyleSheet(f'background-color: none')
        self.bold_active = False
        self.italic_active = False
        self.underlined_active = False
        self.bold.setStyleSheet('background-color: none')
        format.setFontWeight(QtGui.QFont.Normal)
        self.italic.setStyleSheet('background-color: none')
        format.setFontItalic(self.italic_active)
        self.underlined.setStyleSheet('background-color: none')
        format.setFontUnderline(self.underlined_active)
        self.merge_format_on_word_or_selection(format)
        self.line_spacing.setCurrentText("1.0")
        self.font.setCurrentText("Academy Engraved LET")
        self.font_size.setCurrentText("8")
        self.close()


if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    main_window = MainWindow()
    main_window.show()
    sys.exit(app.exec_())