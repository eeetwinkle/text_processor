from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QTextEdit,
                             QPushButton, QFileDialog, QInputDialog, QApplication)
from PyQt5.QtGui import QTextCursor, QTextImageFormat, QPixmap


class TextEditorWithResizableImages(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Текстовый редактор с изменяемыми изображениями")
        self.setGeometry(100, 100, 600, 400)

        layout = QVBoxLayout(self)

        self.text_edit = QTextEdit(self)
        layout.addWidget(self.text_edit)

        self.insert_image_button = QPushButton("Вставить изображение", self)
        self.insert_image_button.clicked.connect(self.insert_image)
        layout.addWidget(self.insert_image_button)

        self.setLayout(layout)

    def insert_image(self):
        """Метод для вставки изображения в текстовый редактор."""
        options = QFileDialog.Options()
        file_name, _ = QFileDialog.getOpenFileName(self, "Выберите изображение", "",
                                                     "Images (*.png *.xpm *.jpg *.jpeg);;All Files (*)", options=options)
        if file_name:
            cursor = self.text_edit.textCursor()
            image_format = QTextImageFormat()
            image_format.setName(file_name)

            # Запрашиваем размер у пользователя
            width, ok = QInputDialog.getInt(self, "Ширина изображения", "Введите ширину:", 100, 1, 3000)
            if ok:
                height, ok = QInputDialog.getInt(self, "Высота изображения", "Введите высоту:", 100, 1, 3000)
                if ok:
                    image_format.setWidth(width)
                    image_format.setHeight(height)

                    cursor.insertImage(image_format)


if __name__ == '__main__':
    import sys

    app = QApplication(sys.argv)
    editor = TextEditorWithResizableImages()
    editor.show()
    sys.exit(app.exec_())


