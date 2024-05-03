import sys
import pathlib
from PyQt5.QtWidgets import (QApplication, QWidget, QVBoxLayout, QLabel, QLineEdit,
                             QPushButton, QFileDialog, QMessageBox, QLabel, QVBoxLayout, QHBoxLayout, QCheckBox)
from PyQt5.QtCore import Qt, QMimeData
from PyQt5.QtGui import QPixmap, QIcon

from txt2epub import Txt2Epub  # Ensure to import your Txt2Epub class

class EpubCreatorGUI(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()
        self.text_file_path = None
        self.cover_image_path = None

    def initUI(self):
        self.setWindowTitle('Text2Epub Converter')
        self.setWindowIcon(QIcon('icon.png'))
        layout = QVBoxLayout()
        self.setAcceptDrops(True)

        # Text File Drop Area
        self.textFileLabel = QLabel('Drag & Drop Text File Here')
        self.textFileLabel.setFixedSize(500, 100)
        self.textFileLabel.setStyleSheet('border: 2px dashed #aaa;')
        self.textFileLabel.setAlignment(Qt.AlignCenter)
        self.textFileLabel.setAcceptDrops(True)
        layout.addWidget(self.textFileLabel)

        # Cover Image Drop Area
        self.coverImageLabel = QLabel('Drag & Drop Cover Image Here')
        self.coverImageLabel.setStyleSheet('border: 2px dashed #aaa;')
        self.coverImageLabel.setAlignment(Qt.AlignCenter)
        self.coverImageLabel.setAcceptDrops(True)
        layout.addWidget(self.coverImageLabel)

        # Title Input
        self.titleInput = QLineEdit()
        self.titleInput.setPlaceholderText('Enter book title')
        layout.addWidget(self.titleInput)

        # Author Input
        self.authorInput = QLineEdit()
        self.authorInput.setPlaceholderText('Enter author name')
        layout.addWidget(self.authorInput)

        # Detect Chapters (Checkbox and Input on the same line)
        self.detectChaptersLayout = QHBoxLayout()
        self.detectChaptersCheckbox = QCheckBox("Detect chapters")
        self.detectChaptersLayout.addWidget(self.detectChaptersCheckbox)

        self.chapterIdentifierInput = QLineEdit()
        self.chapterIdentifierInput.setPlaceholderText("Special characters that identify chapter")
        self.chapterIdentifierInput.setEnabled(False)
        self.chapterIdentifierInput.setStyleSheet("""
            QLineEdit {
                color: #333; /* Text color when enabled */
                background-color: #fff; /* Background when enabled */
            }
            QLineEdit:disabled {
                color: #aaa; /* Text color when disabled */
                background-color: #ddd; /* Background when disabled */
            }
        """)
        self.detectChaptersLayout.addWidget(self.chapterIdentifierInput)
        
        layout.addLayout(self.detectChaptersLayout)

        self.detectChaptersCheckbox.stateChanged.connect(self.toggleChapterIdentifierInput)

        # Convert Button
        self.convertButton = QPushButton('Convert to EPUB')
        self.convertButton.clicked.connect(self.convert_to_epub)
        layout.addWidget(self.convertButton)

        self.setLayout(layout)
        self.setGeometry(300, 300, 500, 400)

    def dragEnterEvent(self, event):
        if event.mimeData().hasImage():
            event.accept()
        elif event.mimeData().hasUrls():
            event.accept()
        else:
            event.ignore()

    def dropEvent(self, event):
        for url in event.mimeData().urls():
            file_path = url.toLocalFile()
            # print(file_path)
            if file_path.lower().endswith('.txt'):
                self.text_file_path = file_path
                self.text_file_path = pathlib.Path(self.text_file_path)
                self.textFileLabel.setText(f'Loaded: {self.text_file_path.name}')
            elif file_path.lower().endswith(('.png', '.jpg', '.jpeg', '.webp')):
                self.cover_image_path = pathlib.Path(file_path)
                pixmap = QPixmap(file_path)
                self.set_image(pixmap)

    def set_image(self, pixmap):
        # Adjust the size of the image
        if pixmap.height() > pixmap.width():
            pixmap = pixmap.scaled(300, 300, Qt.KeepAspectRatio, Qt.SmoothTransformation)
        else:
            pixmap = pixmap.scaled(500, 500, Qt.KeepAspectRatio, Qt.SmoothTransformation)
        print(pixmap.size())
        self.coverImageLabel.setPixmap(pixmap)
        self.coverImageLabel.setFixedSize(pixmap.size())
        # shrink or enlarge the whole window
        self.setFixedHeight(pixmap.height()+250)
    
    def toggleChapterIdentifierInput(self, state):
        # Enable the line edit only if the checkbox is checked
        self.chapterIdentifierInput.setEnabled(state == Qt.Checked)

    def convert_to_epub(self):
        if not self.text_file_path:
            QMessageBox.warning(self, "Warning", "Please provide a text file.")
            return
        
        epub_creator = Txt2Epub(
            book_title=self.titleInput.text(),
            book_author=self.authorInput.text()
        )
        
        output_file = QFileDialog.getSaveFileName(self, 'Save EPUB', '', '*.epub')[0]
        if output_file:
            epub_creator.create_epub(self.text_file_path, self.cover_image_path, pathlib.Path(output_file), self.chapterIdentifierInput.text())
            QMessageBox.information(self, "Success", "The EPUB file has been created successfully.")

if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = EpubCreatorGUI()
    ex.show()
    sys.exit(app.exec_())