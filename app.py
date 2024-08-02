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
from mutagen.id3 import ID3, ID3NoHeaderError, APIC, TIT2, TPE1, TALB, TDRC
from mutagen import File as MutagenFile
import re

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("MP3 Editor")
        self.resize(1024, 768)
        
        with open("style.qss", "r") as file:
            self.setStyleSheet(file.read())

        # Set up the main layout
        self.main_layout = QVBoxLayout()
        self.audio_info_layout = QVBoxLayout()

        self.main_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
    
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
        
        update_audio_info_layout = QVBoxLayout()
        update_audio_info_layout.setObjectName("update_audio_info_layout")
        update_audio_info_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        form_layout = QFormLayout()
        for _tag, value in audio.items():
            tag = COMMON_TAGS.get(_tag)
            if not tag:
                print(_tag)
                continue
            label = QLabel(f"{tag}: ")
            label.setProperty("tag", _tag)
            input = QLineEdit(str(value))
            input.setObjectName("audio-tag-input")
            form_layout.addRow(label, input)
        
        update_audio_info_layout.addLayout(form_layout)

        save_changes_button = QPushButton("Save changes")
        save_changes_button.clicked.connect(lambda: self.update_metadata(audio, form_layout))
        update_audio_info_layout.addWidget(save_changes_button)
        
        self.audio_info_layout.addLayout(update_audio_info_layout)
        self.audio_info_layout.addStretch()
    
    def update_metadata(self, audio: ID3, form_layout: QFormLayout):
        """
        Updates the ID3 tags of the provided audio file based on the values in the form layout.

        This method iterates through the rows of the given form layout, retrieves the tag information from
        the QLabel and QLineEdit widgets, and updates the corresponding ID3 tags in the audio file. After 
        updating the tags, it adds a label indicating a successful/unsuccessful update to the UI if it 
        doesn't already exist.
        """

        for i in range(QFormLayout.rowCount(form_layout)):
            # Get the item at the specified row and role (LabelRole or FieldRole)
            label_widget = form_layout.itemAt(i, QFormLayout.ItemRole.LabelRole).widget()
            field_widget = form_layout.itemAt(i, QFormLayout.ItemRole.FieldRole).widget()
            try:
                self.update_tag(audio, label_widget.property("tag"), field_widget.text())
            except ValueError as e:
                self.add_audio_update_text(str(e))
                return
        self.add_audio_update_text("Successfully updated tags")
        

    def update_tag(self, audio: ID3, tag: str, new_value: str):
        """
        Updates a specific ID3 tag in the given audio file with a new value.
        """
        
        if tag == 'TIT2':
            audio[tag] = TIT2(encoding=3, text=new_value)
        elif tag == 'TPE1':
            audio[tag] = TPE1(encoding=3, text=new_value)
        elif tag == 'TALB':
            audio[tag] = TALB(encoding=3, text=new_value)
        elif tag == 'TDRC':
            if not re.match(r'^\d{4}(-\d{2}){0,2}$', new_value):
                raise ValueError(f"Invalid date format for TDRC tag: {new_value}. Expected format is YYYY, YYYY-MM, or YYYY-MM-DD.")
            audio[tag] = TDRC(encoding=3, text=new_value)
        audio.save()

    def add_audio_update_text(self, text):
        """
        Updates or adds a status label to the UI with the provided text.

        This method creates a QLabel with the given text to display a status message related to audio updates. 
        If a label with the object name "update_text_label" already exists, it updates the text of the existing label. 
        Otherwise, it adds a new QLabel to the `update_audio_info_layout` layout.
        """

        # Create the label for update status
        update_text_label = QLabel(text)
        update_text_label.setObjectName("update_text_label")

        # Find the update_audio_info_layout within the parent widget
        update_audio_info_layout = self.findChild(QVBoxLayout, "update_audio_info_layout")

        # Update the update_text_label if it already exists, otherwise add it
        existing_label = self.findChild(QLabel, "update_text_label")
        if not existing_label:
            update_audio_info_layout.addWidget(update_text_label)
        else:
            existing_label.setText(text)
    


# Create the application instance
app = QApplication(sys.argv)

# Create the main window
window = MainWindow()
window.show()

# Run the application's event loop
sys.exit(app.exec())
