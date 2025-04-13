import sys
from PySide6.QtWidgets import QApplication
from  invoice_system.app.ui.main_Window  import MainWindow
from invoice_system.app.ui.styles import load_stylesheet

if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyleSheet(load_stylesheet())
    window = MainWindow()
    window.show()
    window.showMaximized()
    sys.exit(app.exec())