import sys
import webbrowser
from PyQt5.QtWidgets import QApplication, QTextEdit, QPushButton, QVBoxLayout, QWidget, QInputDialog, QMessageBox
from PyQt5.QtGui import QTextCursor, QTextCharFormat
from PyQt5.QtCore import Qt, QUrl


class TextEditor(QWidget):
    def __init__(self):
        super().__init__()

        self.init_ui()

    def init_ui(self):
        self.setWindowTitle('Текстовый редактор с гиперссылками')

        self.text_edit = QTextEdit(self)
        self.text_edit.setAcceptRichText(True)  # Позволяет использовать HTML-теги

        self.add_link_button = QPushButton('Добавить ссылку', self)
        self.add_link_button.clicked.connect(self.add_link)

        #self.open_link_button = QPushButton('Открыть ссылку', self)
        #self.open_link_button.clicked.connect(self.open_link)
        #self.open_link_button.setEnabled(False)  # Изначально кнопка отключена

        layout = QVBoxLayout()
        layout.addWidget(self.text_edit)
        layout.addWidget(self.add_link_button)
        #layout.addWidget(self.open_link_button)

        self.setLayout(layout)

        # Подключим изменение текста к проверке состояния кнопки
        self.text_edit.selectionChanged.connect(self.update_open_link)

        self.show()

    def add_link(self):
        link_text, ok1 = QInputDialog.getText(self, 'Текст ссылки', 'Введите текст для ссылки:')
        if ok1 and link_text:
            url, ok2 = QInputDialog.getText(self, 'URL ссылки',
                                            'Введите URL для ссылки (например, http://example.com):')
            if ok2 and url:
                cursor = self.text_edit.textCursor()

                # Вставляем текст ссылки с гиперссылкой
                cursor.insertHtml(f'<a href="{url}">{link_text}</a> ')

                # Устанавливаем курсор в конец текста
                self.text_edit.setTextCursor(cursor)

    def update_open_link(self):
        cursor = self.text_edit.textCursor()
        selected_text = cursor.selectedText()  # Получаем выделенный текст
        # Проверяем, является ли выделенный текст гиперссылкой
        if self.is_link_selected(cursor) == True:
            self.open_link()

    def open_link(self):
        cursor = self.text_edit.textCursor()
        if self.is_link_selected(cursor):
            link_format = cursor.charFormat()
            url = link_format.anchorHref()
            if url:
                self.show_link_dialog(url)  # Открываем диалог для перехода по ссылке

    def show_link_dialog(self, url):
        reply = QMessageBox.question(self, 'Переход по ссылке', f'Хотите перейти по ссылке: {url}?',
                                     QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        if reply == QMessageBox.Yes:
            webbrowser.open(QUrl(url).toString())  # Открываем ссылку в браузере

    def is_link_selected(self, cursor):
        # Проверка, является ли выделенный текст гиперссылкой
        cursor.select(QTextCursor.WordUnderCursor)
        link_format = cursor.charFormat()
        return link_format.isAnchor()  # Проверка является ли текст анкором (гиперссылкой)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    editor = TextEditor()
    sys.exit(app.exec_())


