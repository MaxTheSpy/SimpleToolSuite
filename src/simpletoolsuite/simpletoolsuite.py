import warnings
warnings.filterwarnings("ignore", category=DeprecationWarning)

import os
import json
import platform
import sys
import shutil
from PyQt5 import QtWidgets, uic, QtGui, QtCore
from PyQt5.QtWidgets import QCheckBox
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

    # Configuration location
    if system == "Windows":       # Windows
        config_base_dir = os.path.join(home, "AppData", "Local", "SimpleToolSuite")
    elif system == "Darwin":      # MacOS
        config_base_dir = os.path.join(home, "Library", "Application Support", "SimpleToolSuite")
    else:                         # Linux/Unix 
        config_base_dir = os.path.join(home, ".config", "SimpleToolSuite")

    # Plugin location
    if system == "Windows":       # Windows
        plugin_base_dir = os.path.join(config_base_dir, "Plugins")
    elif system == "Darwin":      # MacOS
        plugin_base_dir = os.path.join(config_base_dir, "Plugins")
    else:                         # Linux/Unix
        plugin_base_dir = os.path.join(config_base_dir, "Plugins")

    # Log location
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
        
        """Setup logging"""
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
        self.tab_widget.setCurrentIndex(0) #Set Plugins Tab as the active tab on startup.
        self.tab_widget.setTabVisible(2, False)# Ensure the plugin execution tab is initially hidden
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

        # Discover plugins and find the selected one
        plugins = self.plugin_manager.discover_plugins()
        selected_plugin = next((p for p in plugins if p["name"] == plugin_name), None)

        # Log and return if the plugin is not found
        if not selected_plugin:
            self.sts_logger.error(f"Metadata not found for plugin: {plugin_name}")
            self.description_list.addItem("Error: Metadata not found.")
            return

        metadata_path = os.path.join(selected_plugin["path"], "metadata.json")

        # Log and return if the metadata file does not exist
        if not os.path.exists(metadata_path):
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

        # Check if no plugin is selected and prevent duplicate logs
        if not selected_item:
            existing_warning = [self.description_list.item(i).text() for i in range(self.description_list.count())]
            if "No plugin selected." not in existing_warning:
                self.sts_logger.warning("No plugin selected. Launch Plugin action aborted.")
                self.description_list.addItem("No plugin selected.")
            return

        plugin_name = selected_item.text()
        self.sts_logger.info(f"Launch Plugin button clicked. Selected plugin: '{plugin_name}'.")

        # Discover plugins and log if the plugin is not found
        plugins = self.plugin_manager.discover_plugins()
        selected_plugin = next((p for p in plugins if p["name"] == plugin_name), None)
        if not selected_plugin:
            self.sts_logger.error(f"Plugin '{plugin_name}' not found.")
            self.description_list.addItem("Plugin not found.")
            return

        # Log that the plugin is attempting to launch
        self.sts_logger.info(f"'{plugin_name}' Attempting To Launch.")

        # Load and activate the plugin's virtual environment and module
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
