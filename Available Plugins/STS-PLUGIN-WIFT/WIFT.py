import os
import shutil
import threading
import webbrowser
from flask import Flask, request, render_template, send_from_directory, redirect, url_for
from PyQt5 import QtWidgets, uic, QtCore
from PyQt5.QtWidgets import QMessageBox, QTableWidgetItem
from PyQt5.QtCore import pyqtSignal
from werkzeug.serving import make_server

class ControlledFlaskServer:
    def __init__(self, app, host="0.0.0.0", port=5000):
        self.app = app
        self.host = host
        self.port = port
        self.server = None
        self.thread = None

    def start(self):
        self.server = make_server(self.host, self.port, self.app)
        self.thread = threading.Thread(target=self.server.serve_forever, daemon=True)
        self.thread.start()

    def stop(self):
        if self.server:
            self.server.shutdown()
            self.thread.join()
            self.server = None
            self.thread = None


class WIFTPlugin(QtWidgets.QWidget):
    file_added = pyqtSignal() 
    def __init__(self, parent=None):
        super().__init__(parent)
        self.server_running = threading.Event()
        self.app = Flask(
            __name__,
            template_folder=os.path.join(os.path.dirname(__file__), "WebPage"),
            static_folder=os.path.join(os.path.dirname(__file__), "WebPage")
        )
        self.flask_server = ControlledFlaskServer(self.app)
        self.temp_dir = os.path.join(os.path.dirname(__file__), "WebPage/temp_files")
        os.makedirs(self.temp_dir, exist_ok=True)
        self.file_added.connect(self.update_file_table)
        self.setup_ui()
        self.configure_routes()

    def setup_ui(self):
        try:
            ui_path = os.path.join(os.path.dirname(__file__), "WIFT.ui")
            uic.loadUi(ui_path, self)
            self.start_server_button = self.findChild(QtWidgets.QPushButton, "start_server")
            self.label_status = self.findChild(QtWidgets.QLabel, "label_status")
            self.display_url = self.findChild(QtWidgets.QLineEdit, "display_url")
            self.open_site_button = self.findChild(QtWidgets.QPushButton, "open_site")
            self.file_table = self.findChild(QtWidgets.QTableWidget, "file_table")
            self.start_server_button.clicked.connect(self.toggle_server)
            self.open_site_button.clicked.connect(self.open_website)
            self.file_table.setColumnCount(3)
            self.file_table.setHorizontalHeaderLabels(["Filename", "Type", "Actions"])
            self.file_table.setColumnWidth(2, 200)          # Resize action column
            self.update_status("Stopped", "red")
            self.update_file_table()

        except Exception as e:
            QMessageBox.critical(self, "UI Setup Error", f"Error setting up the UI: {str(e)}")
            raise

    def configure_routes(self):
        @self.app.route('/')
        def index():
            files = os.listdir(self.temp_dir)
            return render_template('index.html', files=files)

        @self.app.route('/upload', methods=['POST'])
        def upload_file():
            file = request.files.get('file')
            if file and file.filename:
                file.save(os.path.join(self.temp_dir, file.filename))
                QtCore.QMetaObject.invokeMethod(self, "file_added", QtCore.Qt.QueuedConnection)
                return redirect(url_for('index'))
            return "No file selected", 400

        @self.app.route('/download/<filename>')
        def download_file(filename):
            return send_from_directory(self.temp_dir, filename, as_attachment=True)

        @self.app.route('/delete/<filename>', methods=['POST'])
        def delete_file(filename):
            file_path = os.path.join(self.temp_dir, filename)
            if os.path.exists(file_path):
                os.remove(file_path)
                self.file_added.emit()  # Update the file table via signal
                return redirect(url_for('index'))
            return "File not found", 404

    def toggle_server(self):
        if self.server_running.is_set():
            self.stop_server()
            self.start_server_button.setText("Start Server")
        else:
            self.start_flask_server()
            self.start_server_button.setText("Stop Server")

    def start_flask_server(self):
        try:
            ip_address = self.get_local_ip_address()
            self.display_url.setText(f"http://{ip_address}:5000")
            self.update_status("Running", "green")
            self.server_running.set()
            self.flask_server.start()
        except Exception as e:
            self.update_status("Problem!", "orange")
            print(f"Server Error: {e}")
            self.server_running.clear()

    def stop_server(self):
        """Stop the Flask server if it is running."""
        if self.server_running.is_set():
            self.flask_server.stop()
            self.server_running.clear()
            self.update_status("Stopped", "red")
            self.display_url.clear()
            print("Flask server stopped.")

    def open_website(self):
        url = self.display_url.text()
        if url:
            webbrowser.open(url)
        else:
            QMessageBox.warning(self, "Error", "No URL to open!")

    def update_file_table(self):
        self.file_table.setRowCount(0)  # Clear the table
        for filename in os.listdir(self.temp_dir):
            row_position = self.file_table.rowCount()
            self.file_table.insertRow(row_position)
            self.file_table.setItem(row_position, 0, QTableWidgetItem(filename))
            file_type = os.path.splitext(filename)[1][1:] or "Unknown"
            self.file_table.setItem(row_position, 1, QTableWidgetItem(file_type))
            button_widget = QtWidgets.QWidget()
            button_layout = QtWidgets.QHBoxLayout(button_widget)
            button_layout.setContentsMargins(0, 0, 0, 0)
            download_button = QtWidgets.QPushButton("Download")
            download_button.clicked.connect(lambda checked, f=filename: self.handle_download(f))
            delete_button = QtWidgets.QPushButton("Delete")
            delete_button.clicked.connect(lambda checked, f=filename: self.handle_delete(f))
            button_layout.addWidget(download_button)
            button_layout.addWidget(delete_button)
            self.file_table.setCellWidget(row_position, 2, button_widget)

    def handle_download(self, filename):
        """Handle file download from the table."""
        file_path = os.path.join(self.temp_dir, filename)
        if os.path.exists(file_path):
            dest = os.path.join(os.path.expanduser("~"), "Downloads", filename)
            shutil.copy(file_path, dest)
            QMessageBox.information(self, "Download", f"File downloaded to {dest}")
        else:
            QMessageBox.warning(self, "Download Error", "File not found!")

    def handle_delete(self, filename):
        """Handle file deletion from the table."""
        file_path = os.path.join(self.temp_dir, filename)
        if os.path.exists(file_path):
            os.remove(file_path)
            self.file_added.emit()  # Update the file table via signal
            QMessageBox.information(self, "Delete", f"File '{filename}' deleted.")
        else:
            QMessageBox.warning(self, "Delete Error", "File not found!")

    def cleanup_temp_files(self):
        for filename in os.listdir(self.temp_dir):
            os.remove(os.path.join(self.temp_dir, filename))

    def update_status(self, status, color):
        self.label_status.setText(status)
        self.label_status.setStyleSheet(f"color: {color};")

    def get_local_ip_address(self):
        import socket
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        try:
            s.connect(("8.8.8.8", 80))
            return s.getsockname()[0]
        except Exception:
            return "127.0.0.1"
        finally:
            s.close()

    def hideEvent(self, event):
        """Override hideEvent to stop Flask server when tab is closed."""
        self.stop_server()
        super().hideEvent(event)

def main(parent_widget):
    try:
        return WIFTPlugin(parent_widget)
    except Exception as e:
        QMessageBox.critical(None, "Plugin Error", f"Failed to load Wi-Fi File Transfer plugin: {str(e)}")
        return None
