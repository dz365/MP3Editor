import sys
from PySide6.QtWidgets import (
    QApplication,
    QMainWindow,
    QPushButton,
    QLabel,
    QVBoxLayout,
    QHBoxLayout,
    QWidget,
    QFileDialog,
    QLineEdit,
    QFormLayout
)
from PySide6.QtGui import QImage, QPixmap
from PySide6.QtCore import Qt
from mutagen.id3 import ID3, ID3NoHeaderError, APIC
from mutagen import File as MutagenFile

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("MP3 Editor")
        self.resize(1024, 768)
        # Set up the main layout
        self.main_layout = QVBoxLayout()
        self.audio_info_layout = QVBoxLayout()
    
        self.file_selected_label = QLabel("No file selected")
        self.main_layout.addWidget(self.file_selected_label)

        # Create a file upload button and connect its clicked signal to a method
        self.file_button = QPushButton("Upload File")
        self.file_button.clicked.connect(self.upload_file)
        self.main_layout.addWidget(self.file_button)

        self.main_layout.addLayout(self.audio_info_layout)

        # Set up a central widget with the layout
        container = QWidget()
        container.setLayout(self.main_layout)
        self.setCentralWidget(container)
    
    # Removes all items from a layout
    def clearLayout(self, layout):
        if layout is not None:
            while layout.count():
                item = layout.takeAt(0)
                widget = item.widget()
                if widget is not None:
                    widget.deleteLater()
                else:
                    self.clearLayout(item.layout())


    def upload_file(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "Open MP3 File", "", "MP3 Files (*.mp3)")
        if not file_path:
            return
        
        try:
            audio = ID3(file_path)
        except ID3NoHeaderError:
            audio = MutagenFile(file_path, easy=True)
            audio.add_tags()
        
        self.main_layout.removeItem(self.audio_info_layout)
        self.clearLayout(self.audio_info_layout)

        self.audio_info_layout = QHBoxLayout()
        self.audio_info_layout.setAlignment(Qt.AlignTop)
        self.audio_info_layout.addStretch()
        self.main_layout.addLayout(self.audio_info_layout)

        COMMON_TAGS = {
            'TIT2': 'Title',
            'TPE1': 'Artist',
            'TALB': 'Album',
            'TDRC': 'Year'
        }

        self.file_selected_label.setText(file_path)


        # Display album cover first
        for tag in audio.values():
            if isinstance(tag, APIC):
                image = QImage()
                image.loadFromData(tag.data)
                pixmap = QPixmap.fromImage(image).scaled(256, 256, Qt.KeepAspectRatio)

                image_label = QLabel()
                image_label.setPixmap(pixmap)
                self.audio_info_layout.addWidget(image_label)
                break
        
        form_layout = QFormLayout()
        for _tag, value in audio.items():
            tag = COMMON_TAGS.get(_tag)
            if not tag:
                print(_tag)
                continue
            label = QLabel(f"{tag}: ")
            input = QLineEdit(str(value))
            input.setStyleSheet("padding: 4px 8px; border-radius: 4px;")
            form_layout.addRow(label, input)
        self.audio_info_layout.addLayout(form_layout)
        self.audio_info_layout.addStretch()
        

# Create the application instance
app = QApplication(sys.argv)

# Create the main window
window = MainWindow()
window.show()

# Run the application's event loop
sys.exit(app.exec())
