import warnings # Remove this later
import os
import tempfile
import qrcode
from PyQt5 import QtWidgets, uic
from PyQt5.QtGui import QPixmap

warnings.simplefilter("ignore", category=DeprecationWarning)  # Remove this later

# https://pypi.org/project/qrcode/

class QRCodeApp(QtWidgets.QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        current_dir = os.path.dirname(os.path.abspath(__file__))
        ui_path = os.path.join(current_dir, "QRCG.ui")
        if os.path.exists(ui_path):
            uic.loadUi(ui_path, self)
        else:
            raise FileNotFoundError(f"UI file not found: {ui_path}")
        self.setup_ui()

    def setup_ui(self):
        # Connect UI elements
        self.lineEdit_qr_data = self.findChild(QtWidgets.QLineEdit, "lineEdit_qr_data")
        self.sel_qr_version = self.findChild(QtWidgets.QComboBox, "sel_qr_version")
        self.lineEdit_file_name = self.findChild(QtWidgets.QLineEdit, "lineEdit_file_name")
        self.lineEdit_box_size = self.findChild(QtWidgets.QLineEdit, "lineEdit_box_size")
        self.lineEdit_border_size = self.findChild(QtWidgets.QLineEdit, "lineEdit_border_size")
        self.button_generate = self.findChild(QtWidgets.QPushButton, "button_generate")
        self.button_save = self.findChild(QtWidgets.QPushButton, "button_save")
        self.label_qr_display = self.findChild(QtWidgets.QLabel, "label_qr_display")
        self.sel_qr_err = self.findChild(QtWidgets.QComboBox, "sel_qr_err")

        # Connect the buttons to the functions
        self.button_generate.clicked.connect(self.generate_qr_code)
        self.button_save.clicked.connect(self.save_qr_code)

        self.temp_file = None

    def generate_qr_code(self):
        qr_data = self.lineEdit_qr_data.text()
        qr_version = self.sel_qr_version.currentText()
        err_correction = self.sel_qr_err.currentText()

        if not qr_data:
            QtWidgets.QMessageBox.warning(self, "Input Error", "QR Data is required!")
            return

        err_correction_map = {
            "Level L  (Approx 7%)": qrcode.constants.ERROR_CORRECT_L,
            "Level M (Approx 15%)": qrcode.constants.ERROR_CORRECT_M,
            "Level Q (Approx 25%)": qrcode.constants.ERROR_CORRECT_Q,
            "Level H (Approx(30%)": qrcode.constants.ERROR_CORRECT_H,
        }
        err_correction_level = err_correction_map.get(err_correction, qrcode.constants.ERROR_CORRECT_L)

        try:
            box_size = int(self.lineEdit_box_size.text())
            border_size = int(self.lineEdit_border_size.text())
        except ValueError:
            QtWidgets.QMessageBox.warning(self, "Input Error", "Box size and border size must be integers!")
            return

        qr = qrcode.QRCode(
            version=int(qr_version),
            error_correction=err_correction_level,
            box_size=box_size,
            border=border_size,
        )

        qr.add_data(qr_data)
        qr.make(fit=True)
        img = qr.make_image(fill_color="black", back_color="white")
        self.temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".png")
        try:
            img.save(self.temp_file.name)
            self.display_qr_code(self.temp_file.name)
        except Exception as e:
            QtWidgets.QMessageBox.critical(self, "Save Error", f"Failed to save QR Code: {str(e)}")

    def display_qr_code(self, filename):
        pixmap = QPixmap(filename)
        self.label_qr_display.setPixmap(pixmap)

    def save_qr_code(self):
        if self.temp_file:
            file_name = self.lineEdit_file_name.text() + ".png"
            output_path = os.path.abspath(file_name)
            try:
                os.rename(self.temp_file.name, output_path)
                QtWidgets.QMessageBox.information(self, "Success", f"QR Code saved at: {output_path}")
                self.temp_file = None
            except Exception as e:
                QtWidgets.QMessageBox.critical(self, "Save Error", f"Failed to save QR Code: {str(e)}")

    def closeEvent(self, event):
        if self.temp_file:
            os.remove(self.temp_file.name)
        event.accept()


def main(parent_widget):               #Entry Point
    return QRCodeApp(parent_widget)
