import warnings
warnings.filterwarnings("ignore", category=DeprecationWarning)

import os
import json
import platform
import sys
import shutil
import zipfile
import subprocess
from PyQt5 import QtWidgets, uic, QtGui, QtCore # type: ignore
from PyQt5.QtWidgets import QCheckBox, QFileDialog, QVBoxLayout, QLabel, QLineEdit, QPushButton, QTextEdit, QDialog # type: ignore
from .pluginmanager import PluginManager
from .sts_logging import setup_logging, initialize_loggers


# Constants
VERSION = "1.0.8"
DEFAULT_CONFIG_NAME = "config.json"
DARK_MODE_STYLE = "dark_mode.css"


def get_default_config_path():
    """Determine the default configuration and plugin directory paths based on the operating system."""
    home = os.path.expanduser("~")
    system = platform.system()

    # Configuration location.
    if system == "Windows":       # Windows
        config_base_dir = os.path.join(home, "AppData", "Local", "SimpleToolSuite")
    elif system == "Darwin":      # MacOS
        config_base_dir = os.path.join(home, "Library", "Application Support", "SimpleToolSuite")
    else:                         # Linux/Unix 
        config_base_dir = os.path.join(home, ".config", "SimpleToolSuite")

    # Plugin Location.
    if system == "Windows":       # Windows
            plugin_base_dir = os.path.join(home, "AppData", "Local", "SimpleToolSuite", "Plugins")
    elif system == "Darwin":      # macOS
        plugin_base_dir = os.path.join(home, "Library", "Application Support", "SimpleToolSuite", "Plugins")
    else:                         # Linux/Unix
        plugin_base_dir = os.path.join(home, ".local", "share", "SimpleToolSuite", "Plugins")

    # Log location.
    if system == "Windows":       # Windows
        log_base_dir = os.path.join(config_base_dir, "Logs")
    elif system == "Darwin":      # MacOS
        log_base_dir = os.path.join(config_base_dir, "Logs")
    else:                         # Linux/Unix
        log_base_dir = os.path.join(config_base_dir, "Logs")

    config_path = os.path.join(config_base_dir, "config.json")
    return config_path, plugin_base_dir, log_base_dir



class SimpleToolSuite(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        self.config_path, self.plugin_dir, self.log_dir = get_default_config_path()
        self.config = self.load_config()

        unified_logger = setup_logging(self.log_dir)
        self.sts_logger, self.plugin_logger = initialize_loggers(unified_logger)

        self.sts_logger.info("SimpleToolSuite initialized.")
        self.sts_logger.info("Plugin manager initialized.")

        self.app_root = getattr(sys, '_MEIPASS', os.path.dirname(os.path.realpath(__file__)))
        uic.loadUi(os.path.join(self.app_root, "main.ui"), self)

        self.setWindowTitle(f"SimpleToolSuite v{VERSION}")
        self.plugin_manager = PluginManager(self.config.get('plugin_location', os.path.join(os.getcwd(), "plugins")))
        self.init_ui_components()
        self.connect_signals()
        self.apply_config()
        self.setup_ui()

    def init_ui_components(self):
        self.tab_widget = self.findChild(QtWidgets.QTabWidget, "tabWidget")
        self.plugin_list = self.findChild(QtWidgets.QListWidget, "list_plugin_widget")
        self.description_list = self.findChild(QtWidgets.QListWidget, "list_desc")
        self.load_button = self.findChild(QtWidgets.QPushButton, "button_load_plugin")
        self.launch_button = self.findChild(QtWidgets.QPushButton, "button_launch_plugin")
        self.download_button = self.findChild(QtWidgets.QPushButton, "button_download_plugin")
        self.button_save_settings = self.findChild(QtWidgets.QPushButton, "button_save_settings")
        self.button_open_plugin = self.findChild(QtWidgets.QPushButton, "button_open_plugin")
        self.line_edit_plugin_loc = self.findChild(QtWidgets.QLineEdit, "lineEdit_plugin_loc")
        self.button_plugin_loc = self.findChild(QtWidgets.QPushButton, "button_plugin_loc")
        self.checkbox_darkmode = self.findChild(QCheckBox, "checkbox_darkmode")
        self.label_plugin_mode = self.findChild(QtWidgets.QLabel, "label_plugin_mode")
        self.button_open_config = self.findChild(QtWidgets.QPushButton, "button_open_config")
        self.button_open_logs = self.findChild(QtWidgets.QPushButton, "button_open_logs")
        self.button_install_zip = self.findChild(QtWidgets.QPushButton, "button_install_zip")
        
        self.tab_widget.setTabsClosable(True)

    def connect_signals(self):
        try:
            self.launch_button.clicked.disconnect()
        except TypeError:
            pass

        self.load_button.clicked.connect(self.reset_plugin_list)
        self.launch_button.clicked.connect(self.launch_plugin)
        self.plugin_list.itemClicked.connect(self.show_metadata)
        self.button_plugin_loc.clicked.connect(self.browse_plugin_location)
        self.button_open_plugin.clicked.connect(self.open_plugin_location)
        self.button_save_settings.clicked.connect(self.save_config_and_plugins)
        self.checkbox_darkmode.stateChanged.connect(self.toggle_dark_mode)
        self.button_open_config.clicked.connect(self.open_config_location)
        self.button_open_logs.clicked.connect(self.open_logs_folder)
        self.button_install_zip.clicked.connect(self.open_install_zip_dialog)

#TODO: This works from the command prompt but not from the appimage. {#c61, 35}
    def open_install_zip_dialog(self):
        self.sts_logger.info("Install From Zip dialog opened.")
        dialog = QDialog(self)
        dialog.setWindowTitle("Install Plugin from Zip")

        layout = QVBoxLayout()

        label = QLabel("Select a Zip File:")
        layout.addWidget(label)

        line_edit = QLineEdit()
        layout.addWidget(line_edit)

        browse_button = QPushButton("Browse")
        browse_button.clicked.connect(lambda: self.browse_zip_file(line_edit))
        layout.addWidget(browse_button)

        install_button = QPushButton("Install")
        install_button.clicked.connect(lambda: self.install_plugin_from_zip(line_edit.text()))
        layout.addWidget(install_button)

        self.progress_output = QTextEdit()
        self.progress_output.setReadOnly(True)
        layout.addWidget(self.progress_output)

        dialog.setLayout(layout)
        dialog.setModal(False)  # Make the dialog non-blocking
        dialog.show()
        self.dialog = dialog  # Keep a reference to the dialog to prevent garbage collection

    def browse_zip_file(self, line_edit):
        self.sts_logger.info("Browsing for zip file.")
        file_path, _ = QFileDialog.getOpenFileName(self, "Select Zip File", "", "Zip Files (*.zip)")
        if file_path:
            line_edit.setText(file_path)


# Broken part {#500, 95}
    def install_plugin_from_zip(self, zip_path):
        if not zip_path or not zipfile.is_zipfile(zip_path):
            self.sts_logger.error("Invalid zip file selected.")
            self.progress_output.append("Invalid zip file selected.")
            return

        plugin_dir = self.plugin_dir  # Default plugin directory
        temp_dir = os.path.join(os.path.expanduser("~"), ".simpletoolsuite", "temp_install")

        venv_dir = None  # Ensure venv_dir is defined even if requirements.txt is missing

        try:
            # Unzip the contents
            self.sts_logger.info("Extracting zip file...")
            self.progress_output.append("Extracting zip file...")
            with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                zip_ref.extractall(temp_dir)
            self.progress_output.append("Zip file extracted.")

            # Check the extracted structure
            extracted_contents = os.listdir(temp_dir)
            if len(extracted_contents) != 1 or not os.path.isdir(os.path.join(temp_dir, extracted_contents[0])):
                raise ValueError("Unexpected ZIP structure. Expected a single top-level directory.")
            
            extracted_dir = os.path.join(temp_dir, extracted_contents[0])
            requirements_file = os.path.join(extracted_dir, "requirements.txt")

            # Create virtual environments
            venv_dir = os.path.join(extracted_dir, ".venv")
            if not os.path.exists(venv_dir):
                self.sts_logger.info("Creating virtual environment...")
                self.progress_output.append("Creating virtual environment...")
                try:
                    # Dynamically resolve the Python executable from the AppImage's APPDIR environment
                    appdir = os.environ.get("APPDIR", "/tmp/.mount_SimpleToolSuite")
                    python_executable = shutil.which("python3") or os.path.join(appdir, "opt/python3.12/bin/python3.12")

                    
                    if not os.path.exists(python_executable):
                        raise RuntimeError(f"Python executable not found at: {python_executable}")

                    self.sts_logger.debug(f"Using Python executable: {python_executable}")

                    # Create the virtual environment
                    subprocess.check_call([python_executable, "-m", "venv", venv_dir])
                    self.progress_output.append("Virtual environment created.")

                    # Ensure pip is installed and upgraded
                    python_venv_executable = os.path.join(venv_dir, "bin", "python")
                    subprocess.check_call([python_venv_executable, "-m", "ensurepip", "--upgrade", "--default-pip"])
                    subprocess.check_call([python_venv_executable, "-m", "pip", "install", "--upgrade", "pip"])
                    self.progress_output.append("Pip installed and upgraded.")
                    self.sts_logger.info("Pip successfully installed and upgraded.")

                except subprocess.CalledProcessError as venv_error:
                    self.sts_logger.error(f"Virtual environment creation failed: {venv_error}")
                    self.progress_output.append(f"Error: Failed to create virtual environment: {venv_error}")
                    raise RuntimeError(f"Failed to create virtual environment: {venv_error}")


            # Install dependencies if requirements.txt exists
            if os.path.exists(requirements_file):
                self.sts_logger.info("Installing dependencies...")
                self.progress_output.append("Installing dependencies...")
                try:
                    subprocess.check_call([
                        os.path.join(venv_dir, "bin", "pip"), "install", "-r", requirements_file
                    ])
                    self.progress_output.append("Dependencies installed.")
                except subprocess.CalledProcessError as pip_error:
                    raise RuntimeError(f"Failed to install dependencies: {pip_error}")
            else:
                self.sts_logger.warning("No requirements.txt found. Skipping dependency installation.")
                self.progress_output.append("No requirements.txt found. Skipping dependency installation.")

            # Move the plugin to the plugin directory
            self.sts_logger.info("Moving plugin to final directory...")
            self.progress_output.append("Moving plugin to final directory...")
            final_plugin_dir = os.path.join(plugin_dir, os.path.basename(extracted_dir))
            if os.path.exists(final_plugin_dir):
                shutil.rmtree(final_plugin_dir)
            shutil.move(extracted_dir, final_plugin_dir)
            self.config['plugin_location'] = final_plugin_dir
            self.save_config()
            self.progress_output.append("Plugin moved to final directory.")
            self.sts_logger.info("Plugin installed successfully.")
            self.progress_output.append("Plugin installed successfully.")

        except Exception as e:
            self.sts_logger.error(f"Error during installation: {e}")
            self.progress_output.append(f"Error during installation: {e}")

        finally:
            if os.path.exists(temp_dir):
                shutil.rmtree(temp_dir)


    def load_config(self):
        """Load the configuration file, creating a default if it does not exist."""
        self.config_path, default_plugin_dir, _ = get_default_config_path()
        config_dir = os.path.dirname(self.config_path)

        if not os.path.exists(config_dir):
            try:
                os.makedirs(config_dir)
            except OSError as e:
                self.sts_logger.error(f"Failed to create configuration directory: {e}")
                return {}

        if not os.path.exists(self.config_path):
            default_config = {
                "dark_mode": False,
                "plugin_location": default_plugin_dir
                 }
            try:
                with open(self.config_path, 'w') as f:
                    json.dump(default_config, f, indent=4)
            except IOError as e:
                self.sts_logger.error(f"Failed to create configuration file: {e}")
                return default_config

        try:
            with open(self.config_path, 'r') as f:
                return json.load(f)
        except (IOError, json.JSONDecodeError) as e:
            self.sts_logger.error(f"Failed to load configuration file: {e}")
            return {}


    def save_config(self):
        """Save the current configuration."""
        try:
            with open(self.config_path, 'w') as f:
                json.dump(self.config, f, indent=4)
            self.sts_logger.info("Configuration saved successfully.")
        except IOError as e:
            self.sts_logger.error(f"Failed to save configuration file: {e}")

    def apply_config(self):
        self.line_edit_plugin_loc.setText(self.config.get('plugin_location', os.path.join(os.getcwd(), "plugins")))
        dark_mode_enabled = self.config.get('dark_mode', False)
        self.checkbox_darkmode.setChecked(dark_mode_enabled)
        self.apply_style(dark_mode_enabled)

    def apply_style(self, dark_mode_enabled):
        style_sheet = os.path.join(self.app_root, 'dark_mode.css') if dark_mode_enabled else os.path.join(self.app_root, 'light_mode.css')
        if os.path.exists(style_sheet):
            with open(style_sheet, "r") as file:
                self.setStyleSheet(file.read())

    def setup_ui(self):
        self.populate_plugins()
        self.tab_widget.setTabText(0, "Plugins")
        self.tab_widget.setTabText(1, "Settings")
        self.tab_widget.setTabsClosable(True)

        # Hide close buttons on desired tabs (plugins and settings)
        self.tab_widget.tabBar().setTabButton(0, QtWidgets.QTabBar.RightSide, None)
        self.tab_widget.tabBar().setTabButton(1, QtWidgets.QTabBar.RightSide, None)
        self.tab_widget.setCurrentIndex(0)            # Set Plugins Tab as the active tab on startup.
        self.tab_widget.setTabVisible(2, False)       # Ensure the plugin execution tab is initially hidden
        self.tab_widget.tabCloseRequested.connect(self.handle_tab_close)
        self.load_button.clicked.connect(self.reset_plugin_list)

    def populate_plugins(self):
        plugins = self.plugin_manager.discover_plugins()
        if not plugins:
            self.sts_logger.warning("No plugins found in the plugin directory.")
        self.plugin_list.clear()
        for plugin in plugins:
            self.plugin_list.addItem(plugin["name"])

    def reset_plugin_list(self):
        self.populate_plugins()

    def show_metadata(self, item):
        """Display plugin metadata in the description list and log any issues."""
        self.description_list.clear()
        plugin_name = item.text()
        plugins = self.plugin_manager.discover_plugins()     # Discover plugins and find the selected one
        selected_plugin = next((p for p in plugins if p["name"] == plugin_name), None)

        if not selected_plugin:     # Log and return if the plugin is not found
            self.sts_logger.error(f"Metadata not found for plugin: {plugin_name}")
            self.description_list.addItem("Error: Metadata not found.")
            return

        metadata_path = os.path.join(selected_plugin["path"], "metadata.json")

        if not os.path.exists(metadata_path):   # Log and return if the metadata file does not exist
            self.sts_logger.error(f"Missing metadata.json for plugin: {plugin_name}")
            self.description_list.addItem("Error: Missing metadata.json.")
            return

        try:
            # Try to load the metadata JSON file
            with open(metadata_path, "r") as meta_file:
                metadata = json.load(meta_file)
        except (IOError, json.JSONDecodeError) as e:
            self.sts_logger.error(f"Failed to load metadata for plugin '{plugin_name}': {e}")
            self.description_list.addItem(f"Error: Failed to load metadata ({e}).")
            return

        # Fields to display in the description list
        fields_to_display = {
            "name": "Name",
            "version": "Version",
            "author": "Author",
            "description": "Description"
            }

        # Add metadata fields to the description list
        if metadata:
            for key, display_name in fields_to_display.items():
                if key in metadata:
                    value = metadata[key]
                    self.description_list.addItem(f"{display_name}: {value}")


    def browse_plugin_location(self):
        dir_ = QtWidgets.QFileDialog.getExistingDirectory(self, "Select Plugin Directory", self.line_edit_plugin_loc.text() or os.getcwd())
        if dir_:
            self.line_edit_plugin_loc.setText(dir_)
            self.config['plugin_location'] = dir_

    def save_config_and_plugins(self):
        new_plugin_location = self.line_edit_plugin_loc.text().strip()

        if new_plugin_location:
            if not os.path.exists(new_plugin_location):
                os.makedirs(new_plugin_location)

            self.move_plugins(new_plugin_location)
            self.plugin_manager.plugin_dir = new_plugin_location
            self.config['plugin_location'] = new_plugin_location
            self.save_config()
            self.populate_plugins()

    def move_plugins(self, new_plugin_location):
        current_plugin_location = self.plugin_manager.plugin_dir
        if os.path.exists(current_plugin_location):
            for plugin in os.listdir(current_plugin_location):
                plugin_path = os.path.join(current_plugin_location, plugin)
                new_path = os.path.join(new_plugin_location, plugin)
                if os.path.isdir(plugin_path):
                    shutil.move(plugin_path, new_path)

    def open_plugin_location(self):
        dir_ = os.path.abspath(self.line_edit_plugin_loc.text().strip())
        if os.path.exists(dir_):
            QtGui.QDesktopServices.openUrl(QtCore.QUrl.fromLocalFile(dir_))

    def open_logs_folder(self):
        """Open the logs folder."""
        if os.path.exists(self.log_dir):
            QtGui.QDesktopServices.openUrl(QtCore.QUrl.fromLocalFile(self.log_dir))
            self.sts_logger.info("Logs folder opened successfully.")
        else:
            self.sts_logger.error("Logs folder does not exist.")
            QtWidgets.QMessageBox.warning(self, "Error", "Logs folder does not exist.")


    def open_config_location(self):
        config_dir = os.path.abspath(os.path.dirname(self.config_path))
        if os.path.exists(config_dir):
            QtGui.QDesktopServices.openUrl(QtCore.QUrl.fromLocalFile(config_dir))

    def launch_plugin(self):
        """Launch the selected plugin."""
        selected_item = self.plugin_list.currentItem()

        if not selected_item:     # Check if no plugin is selected and prevent duplicate logs
            existing_warning = [self.description_list.item(i).text() for i in range(self.description_list.count())]
            if "No plugin selected." not in existing_warning:
                self.sts_logger.warning("No plugin selected. Launch Plugin action aborted.")
                self.description_list.addItem("No plugin selected.")
            return

        plugin_name = selected_item.text()
        self.sts_logger.info(f"Launch Plugin button clicked. Selected plugin: '{plugin_name}'.")

        plugins = self.plugin_manager.discover_plugins()     # Discover plugins and log if the plugin is not found
        selected_plugin = next((p for p in plugins if p["name"] == plugin_name), None)
        if not selected_plugin:
            self.sts_logger.error(f"Plugin '{plugin_name}' not found.")
            self.description_list.addItem("Plugin not found.")
            return

        self.sts_logger.info(f"'{plugin_name}' Attempting To Launch.") # Log that the plugin is attempting to launch

        """Load and activate the plugin's virtual environment and module"""
        module = self.plugin_manager.load_plugin(selected_plugin["path"], selected_plugin["main"])
        if module and hasattr(module, "main"):
            self.sts_logger.info(f"'{plugin_name}' Launched Successfully.")
            scroll_area = self.findChild(QtWidgets.QScrollArea, "scroll_plugin_container")
            if scroll_area:
                previous_widget = scroll_area.takeWidget()
                if previous_widget:
                    previous_widget.deleteLater()

                scroll_area_widget = QtWidgets.QWidget()
                scroll_area_widget.setLayout(QtWidgets.QVBoxLayout())
                scroll_area.setWidget(scroll_area_widget)

                # Pass the logger to the plugin's main function 
                widget = module.main(parent_widget=scroll_area_widget, parent_logger=self.plugin_logger)

                if isinstance(widget, QtWidgets.QWidget):
                    scroll_area_widget.layout().addWidget(widget)

                self.tab_widget.setTabText(2, plugin_name)
                self.tab_widget.setTabVisible(2, True)
                self.tab_widget.setCurrentIndex(2)
        else:
            self.sts_logger.error(f"'{plugin_name}' Failed To Launch. No 'main' function found.")
            self.description_list.addItem("Plugin does not have a main function.")


    def handle_tab_close(self, index):
        """Handle tab closing by clearing and hiding tab 2."""
        if index == 2:  # Check if it's the plugin execution tab
            plugin_name = self.tab_widget.tabText(index)  # Get the plugin name from the tab text
            self.clear_and_hide_tab(index)
            self.sts_logger.info(f"'{plugin_name}' Closed Successfully.")  # Log the closure
            self.tab_widget.setCurrentIndex(0)  # Set the active tab back to the Plugins tab

    def clear_and_hide_tab(self, index):
        """Clear tab contents and hide the tab."""
        scroll_area = self.findChild(QtWidgets.QScrollArea, "scroll_plugin_container")
        if scroll_area:
            scroll_area_widget = scroll_area.findChild(QtWidgets.QWidget, "scrollAreaWidgetContents")
            if scroll_area_widget:
                # Clear all widgets inside the scroll area
                layout = scroll_area_widget.layout()
                if layout:
                    self.clear_layout(layout)
        self.tab_widget.setTabVisible(index, False)  # Hide the tab

    def clear_layout(self, layout):
        """Remove all widgets from a layout."""
        if layout is not None:
            while layout.count():
                child = layout.takeAt(0)
                if child.widget() is not None:
                    child.widget().deleteLater()


    def toggle_dark_mode(self, state):
        enabled = state == QtCore.Qt.Checked
        self.config['dark_mode'] = enabled
        self.save_config()
        self.apply_style(enabled)

    def closeEvent(self, event):
        self.sts_logger.info("SimpleToolSuite Application Closed.")
        super().closeEvent(event)

def main():
    app = QtWidgets.QApplication([])
    window = SimpleToolSuite()
    window.show()
    app.exec_()

if __name__ == "__main__":
    main()
