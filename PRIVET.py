import sys
import re
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QTextEdit, QLineEdit, QPushButton, QCheckBox, QMessageBox

class TextSearchEditor(QWidget):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Текстовый редактор")
        self.setGeometry(100, 100, 600, 400)

        # Основной компоновщик
        self.layout = QVBoxLayout(self)

        # Создание текстового редактора
        self.text_edit = QTextEdit(self)
        self.layout.addWidget(self.text_edit)

        # Кнопка для открытия окна поиска
        self.open_search_button = QPushButton("Открыть окно поиска", self)
        self.open_search_button.clicked.connect(self.open_search_window)
        self.layout.addWidget(self.open_search_button)

        # Кнопка для открытия окна замены
        self.open_replace_button = QPushButton("Открыть окно замены", self)
        self.open_replace_button.clicked.connect(self.open_replace_window)
        self.layout.addWidget(self.open_replace_button)

        self.setLayout(self.layout)

    def open_search_window(self):
        """Открывает новое окно для поиска текста."""
        self.search_window = SearchWindow(self.text_edit)
        self.search_window.show()

    def open_replace_window(self):
        """Открывает новое окно для поиска текста."""
        self.replace_window = ReplaceWindow(self.text_edit)
        self.replace_window.show()

class SearchWindow(QWidget):
    def __init__(self, text_edit):
        super().__init__()
        self.text_edit = text_edit
        self.found_positions = []  # Список для хранения позиций найденных слов
        self.current_index = -1  # Индекс для текущего найденного слова

        # Основной компоновщик
        self.layout = QVBoxLayout(self)
        self.setWindowTitle("Поиск текста")
        self.setGeometry(200, 200, 400, 200)

        # Поле для ввода текста для поиска
        self.search_input = QLineEdit(self)
        self.layout.addWidget(self.search_input)

        # Чекбоксы для настроек поиска
        self.case_sensitive_checkbox = QCheckBox("Учитывать регистр")
        self.layout.addWidget(self.case_sensitive_checkbox)

        self.whole_word_checkbox = QCheckBox("Слово целиком")
        self.layout.addWidget(self.whole_word_checkbox)

        # Кнопка поиска
        self.find_button = QPushButton("Найти")
        self.find_button.clicked.connect(self.perform_search)
        self.layout.addWidget(self.find_button)

        # Кнопки навигации
        self.next_button = QPushButton("Следующее")
        self.next_button.clicked.connect(self.navigate_to_next)
        self.layout.addWidget(self.next_button)

        self.prev_button = QPushButton("Предыдущее")
        self.prev_button.clicked.connect(self.navigate_to_previous)
        self.layout.addWidget(self.prev_button)

        self.setLayout(self.layout)

    def perform_search(self):
        """Метод, выполняющий поиск по тексту."""
        search_text = self.search_input.text()
        if self.case_sensitive_checkbox.isChecked():
            flags = 0
        else:
            flags = re.IGNORECASE  # Учитываем регистр иначе

        whole_word = self.whole_word_checkbox.isChecked()
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

    def highlight_current_word(self):
        """Метод для выделения текущего найденного слова."""
        self.clear_highlight()  # Сначала снимаем выделение

        if self.current_index >= 0 and self.current_index < len(self.found_positions):
            cursor = self.text_edit.textCursor()
            pos = self.found_positions[self.current_index]
            cursor.setPosition(pos)
            cursor.movePosition(cursor.Right, cursor.KeepAnchor, len(self.search_input.text()))
            self.text_edit.setTextCursor(cursor)
            self.text_edit.setFocus()

    def clear_highlight(self):
        """Метод для снятия выделения."""
        cursor = self.text_edit.textCursor()
        cursor.clearSelection()
        self.text_edit.setTextCursor(cursor)

    def show_message(self, message):
        """Метод для отображения сообщения в диалоговом окне."""
        msg_box = QMessageBox()
        msg_box.setText(message)
        msg_box.exec_()

    def navigate_to_next(self):
        """Навигация к следующему найденному слову."""
        if not self.found_positions:
            return
        self.current_index = (self.current_index + 1) % len(self.found_positions)
        self.highlight_current_word()

    def navigate_to_previous(self):
        """Навигация к предыдущему найденному слову."""
        if not self.found_positions:
            return
        self.current_index = (self.current_index - 1) % len(self.found_positions)
        self.highlight_current_word()


class ReplaceWindow(QWidget):
    def __init__(self, text_edit):
        super().__init__()
        self.text_edit = text_edit

        # Основной компоновщик
        self.layout = QVBoxLayout(self)
        self.setWindowTitle("Замена текста")
        self.setGeometry(200, 200, 400, 200)

        # Поле для ввода слова для замены
        self.word_to_replace_input = QLineEdit(self)
        self.word_to_replace_input.setPlaceholderText("Слово для замены")
        self.layout.addWidget(self.word_to_replace_input)

        # Поле для ввода слова, на которое будем заменять
        self.replacement_word_input = QLineEdit(self)
        self.replacement_word_input.setPlaceholderText("Слово замены")
        self.layout.addWidget(self.replacement_word_input)

        # Чекбоксы для настроек поиска
        self.case_sensitive_checkbox = QCheckBox("Учитывать регистр")
        self.layout.addWidget(self.case_sensitive_checkbox)

        self.whole_word_checkbox = QCheckBox("Слово целиком")
        self.layout.addWidget(self.whole_word_checkbox)

        # Кнопка для замены
        self.replace_button = QPushButton("Заменить все")
        self.replace_button.clicked.connect(self.replace_all)
        self.layout.addWidget(self.replace_button)

        self.setLayout(self.layout)

    def replace_all(self):
        """Метод, выполняющий замену всех найденных слов."""
        word_to_replace = self.word_to_replace_input.text()
        replacement_word = self.replacement_word_input.text()

        if not word_to_replace:
            self.show_message("Пожалуйста, введите слово для замены.")
            return

        if self.case_sensitive_checkbox.isChecked():
            flags = 0
        else:
            flags = re.IGNORECASE  # Учитываем регистр иначе

        whole_word = self.whole_word_checkbox.isChecked()
        pattern = word_to_replace
        if whole_word:
            pattern = r'\b' + re.escape(word_to_replace) + r'\b'

        text = self.text_edit.toPlainText()
        new_text = re.sub(pattern, replacement_word, text, flags=flags)
        self.text_edit.setPlainText(new_text)

        self.show_message(f"Все вхождения '{word_to_replace}' заменены на '{replacement_word}'.")

    def show_message(self, message):
        """Метод для отображения сообщения в диалоговом окне."""
        msg_box = QMessageBox()
        msg_box.setText(message)
        msg_box.exec_()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    editor = TextSearchEditor()
    editor.show()
    sys.exit(app.exec_())


