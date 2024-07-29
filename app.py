import sys
from PySide6.QtWidgets import QApplication, QMainWindow, QPushButton, QLabel, QVBoxLayout, QWidget, QFileDialog
from mutagen.id3 import ID3, ID3NoHeaderError, APIC

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("MP3 Editor")

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

    def button_clicked(self):
        self.label.setText("Button clicked!")

    def upload_file(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "Open MP3 File", "", "MP3 Files (*.mp3)")
        if not file_path:
            return
        
        try:
            audio = ID3(file_path)
        except ID3NoHeaderError:
            audio = mutagen.File(file_path, easy=True)
            audio.add_tags()
        
        for i in reversed(range(self.audio_info_layout.count())): 
            self.audio_info_layout.itemAt(i).widget().setParent(None)

        COMMON_TAGS = {
            'TIT2': 'Title',
            'TPE1': 'Artist',
            'TALB': 'Album',
            'TDRC': 'Year'
        }

        self.file_selected_label.setText(file_path)
        for _tag, value in audio.items():
            if (type(value) == APIC): continue
            tag = COMMON_TAGS.get(_tag)
            if not tag:
                print(_tag)
                continue
            ID3_value = QLabel(f"{tag}: {value}")
            self.audio_info_layout.addWidget(ID3_value)
        

# Create the application instance
app = QApplication(sys.argv)

# Create the main window
window = MainWindow()
window.show()

# Run the application's event loop
sys.exit(app.exec())
