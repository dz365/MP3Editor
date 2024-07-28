import sys
from PySide6.QtWidgets import QApplication, QMainWindow, QPushButton, QLabel, QVBoxLayout, QWidget

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("MP3 Editor")

        # Set up the main layout
        layout = QVBoxLayout()

        # Create a label and add it to the layout
        self.label = QLabel("Hello, PySide6!")
        layout.addWidget(self.label)

        # Create a button and connect its clicked signal to a method
        self.button = QPushButton("Click me!")
        self.button.clicked.connect(self.button_clicked)
        layout.addWidget(self.button)

        # Set up a central widget with the layout
        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)

    def button_clicked(self):
        self.label.setText("Button clicked!")

# Create the application instance
app = QApplication(sys.argv)

# Create the main window
window = MainWindow()
window.show()

# Run the application's event loop
sys.exit(app.exec())
