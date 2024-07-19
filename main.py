import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QTextEdit, QAction, QFileDialog, QColorDialog, QInputDialog
from PyQt5.QtGui import QFont, QColor, QTextCursor, QImage, QTextImageFormat


class TextProcessor(QMainWindow):
    def __init__(self):
        super().__init__()

        self.initUI()

    def initUI(self):
        self.textEdit = QTextEdit()
        self.setCentralWidget(self.textEdit)

        boldAction = QAction('Bold', self)
        boldAction.triggered.connect(self.boldText)

        italicAction = QAction('Italic', self)
        italicAction.triggered.connect(self.italicText)

        underlineAction = QAction('Underline', self)
        underlineAction.triggered.connect(self.underlineText)

        fontAction = QAction('Change Font', self)
        fontAction.triggered.connect(self.changeFont)

        colorAction = QAction('Change Text Color', self)
        colorAction.triggered.connect(self.changeColor)

        imageAction = QAction('Insert Image', self)
        imageAction.triggered.connect(self.insertImage)

        saveAction = QAction('Save', self)
        saveAction.triggered.connect(self.saveFile)

        self.toolbar = self.addToolBar('Formatting')
        self.toolbar.addAction(boldAction)
        self.toolbar.addAction(italicAction)
        self.toolbar.addAction(underlineAction)
        self.toolbar.addAction(fontAction)
        self.toolbar.addAction(colorAction)
        self.toolbar.addAction(imageAction)
        self.toolbar.addAction(saveAction)

        self.setWindowTitle('Text Processor')
        self.show()

    def boldText(self):
        boldFont = self.textEdit.font()
        boldFont.setBold(True)
        self.textEdit.setFont(boldFont)

    def italicText(self):
        italicFont = self.textEdit.font()
        italicFont.setItalic(True)
        self.textEdit.setFont(italicFont)

    def underlineText(self):
        underlinedFont = self.textEdit.font()
        underlinedFont.setUnderline(True)
        self.textEdit.setFont(underlinedFont)

    def changeFont(self):
        font, ok = QFont.getFont()
        if ok:
            self.textEdit.setFont(font)

    def changeColor(self):
        color = QColorDialog.getColor()
        if color.isValid():
            self.textEdit.setTextColor(color)

    def insertImage(self):
        fileName, _ = QFileDialog.getOpenFileName(self, "Insert Image", "", "Images (*.png *.jpg *.jpeg)")
        if fileName:
            image = QImage(fileName)
            cursor = self.textEdit.textCursor()
            imageFormat = QTextImageFormat()
            imageFormat.setWidth(image.width())
            imageFormat.setHeight(image.height())
            imageFormat.setName(fileName)
            cursor.insertImage(imageFormat)

            # Ask user for image width and height
            width, ok = QInputDialog.getInt(self, "Image Width", "Enter image width:")
            if ok:
                imageFormat.setWidth(width)
            height, ok = QInputDialog.getInt(self, "Image Height", "Enter image height:")
            if ok:
                imageFormat.setHeight(height)

            cursor.insertImage(imageFormat)

    def saveFile(self):
        fileName, _ = QFileDialog.getSaveFileName(self, "Save File", "", "Text Files (*.txt)")
        if fileName:
            with open(fileName, 'w') as file:
                text = self.textEdit.toPlainText()
                file.write(text)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    tp = TextProcessor()
    sys.exit(app.exec_())

# что-то добавила