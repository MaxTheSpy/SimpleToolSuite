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

# Constants
VERSION = "1.0.8"
DEFAULT_CONFIG_NAME = "config.json"
DARK_MODE_STYLE = "dark_mode.css"

def get_default_config_path():
    """Determine the default configuration and plugin directory paths based on the operating system."""
    home = os.path.expanduser("~")
    system = platform.system()

    if system == "Windows":
        config_base_dir = os.path.join(home, "AppData", "Local", "SimpleToolSuite")
    elif system == "Darwin":
        config_base_dir = os.path.join(home, "Library", "Application Support", "SimpleToolSuite")
    else:
        config_base_dir = os.path.join(home, ".config", "SimpleToolSuite")

    if system == "Windows":
        plugin_base_dir = os.path.join(home, "AppData", "Local", "SimpleToolSuite", "Plugins")
    elif system == "Darwin":
        plugin_base_dir = os.path.join(home, "Library", "Application Support", "SimpleToolSuite", "Plugins")
    else:
        plugin_base_dir = os.path.join(home, ".local", "share", "SimpleToolSuite", "Plugins")

    config_path = os.path.join(config_base_dir, "config.json")
    return config_path, plugin_base_dir

class SimpleToolSuite(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        self.config_path = get_default_config_path()
        self.config = self.load_config()
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
        self.tab_widget.setTabsClosable(True)

    def connect_signals(self):
        self.load_button.clicked.connect(self.reset_plugin_list)
        self.launch_button.clicked.connect(self.launch_plugin)
        self.plugin_list.itemClicked.connect(self.show_metadata)
        self.button_plugin_loc.clicked.connect(self.browse_plugin_location)
        self.button_open_plugin.clicked.connect(self.open_plugin_location)
        self.button_save_settings.clicked.connect(self.save_config_and_plugins)
        self.checkbox_darkmode.stateChanged.connect(self.toggle_dark_mode)
        self.button_open_config.clicked.connect(self.open_config_location)

    def load_config(self):
        self.config_path, default_plugin_dir = get_default_config_path()
        config_dir = os.path.dirname(self.config_path)

        if not os.path.exists(config_dir):
            os.makedirs(config_dir)

        if not os.path.exists(self.config_path):
            default_config = {
                "dark_mode": False,
                "plugin_location": default_plugin_dir
            }
            with open(self.config_path, 'w') as f:
                json.dump(default_config, f, indent=4)
            return default_config

        with open(self.config_path, 'r') as f:
            return json.load(f)

    def save_config(self):
        with open(self.config_path, 'w') as f:
            json.dump(self.config, f, indent=4)

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
        self.launch_button.clicked.connect(self.launch_plugin)

    def populate_plugins(self):
        plugins = self.plugin_manager.discover_plugins()
        self.plugin_list.clear()
        for plugin in plugins:
            self.plugin_list.addItem(plugin["name"])

    def reset_plugin_list(self):
        self.populate_plugins()

    def show_metadata(self, item):
        self.description_list.clear()
        plugin_name = item.text()

        plugins = self.plugin_manager.discover_plugins()
        selected_plugin = next((p for p in plugins if p["name"] == plugin_name), None)

        if selected_plugin:
            metadata_path = os.path.join(selected_plugin["path"], "metadata.json")
            if os.path.exists(metadata_path):
                with open(metadata_path, "r") as meta_file:
                    metadata = json.load(meta_file)

        fields_to_display = {
            "name": "Name",
            "version": "Version",
            "author": "Author",
            "description": "Description"
        }

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

    def open_config_location(self):
        config_dir = os.path.abspath(os.path.dirname(self.config_path))
        if os.path.exists(config_dir):
            QtGui.QDesktopServices.openUrl(QtCore.QUrl.fromLocalFile(config_dir))

    def launch_plugin(self):
        """Launch the selected plugin."""
        selected_item = self.plugin_list.currentItem()
        if not selected_item:
            self.description_list.addItem("No plugin selected.")
            return
            
        plugin_name = selected_item.text()
        plugins = self.plugin_manager.discover_plugins()
        selected_plugin = next((p for p in plugins if p["name"] == plugin_name), None)
        if not selected_plugin:
            self.description_list.addItem("Plugin not found.")
            return

        # Load and activate the plugin's virtual environment and module
        module = self.plugin_manager.load_plugin(selected_plugin["path"], selected_plugin["main"])
        if module and hasattr(module, "main"):
            scroll_area = self.findChild(QtWidgets.QScrollArea, "scroll_plugin_container")
            if scroll_area:
                # Clear existing content
                previous_widget = scroll_area.takeWidget()
                if previous_widget:
                    previous_widget.deleteLater()

                scroll_area_widget = QtWidgets.QWidget()
                scroll_area_widget.setLayout(QtWidgets.QVBoxLayout())
                scroll_area.setWidget(scroll_area_widget)

                # Instantiate and place the plugin UI
                widget = module.main(scroll_area_widget)

                # Ensure the correct hierarchy
                if isinstance(widget, QtWidgets.QWidget):
                    scroll_area_widget.layout().addWidget(widget)

                self.tab_widget.setTabText(2, plugin_name)
                self.tab_widget.setTabVisible(2, True)
                self.tab_widget.setCurrentIndex(2)
        else:
            self.description_list.addItem("Plugin does not have a main function.")

    def handle_tab_close(self, index):
        """Handle tab closing by clearing and hiding tab 2."""
        if index == 2:  # Check if it's the plugin execution tab
            self.clear_and_hide_tab(index)
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

def main():
    app = QtWidgets.QApplication([])
    window = SimpleToolSuite()
    window.show()
    app.exec_()

if __name__ == "__main__":
    main()
