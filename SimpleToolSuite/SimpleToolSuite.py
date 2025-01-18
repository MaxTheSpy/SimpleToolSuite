import warnings
warnings.filterwarnings("ignore", category=DeprecationWarning)

import os
import json
import platform
import requests
import shutil
from PyQt5 import QtWidgets, uic, QtGui, QtCore
from PyQt5.QtWidgets import QCheckBox
from PluginManager import PluginManager

# Constants
VERSION = "1.0.4"
DEFAULT_CONFIG_NAME = "config.json"
DARK_MODE_STYLE = "dark_mode.css"
GITHUB_API_URL = "https://api.github.com/repos/MaxTheSpy/SimpleToolSuite/contents/Available%20Plugins"

def get_default_config_path():
    """Determine the default configuration file path based on the operating system."""
    home = os.path.expanduser("~")
    system = platform.system()

    if system == "Windows":
        return os.path.join(home, "AppData", "Local", "SimpleToolSuite", DEFAULT_CONFIG_NAME)
    elif system == "Darwin":  # macOS
        return os.path.join(home, "Library", "Application Support", "SimpleToolSuite", DEFAULT_CONFIG_NAME)
    else:  # Assuming Linux and other UNIX-like systems
        return os.path.join(home, ".config", "SimpleToolSuite", DEFAULT_CONFIG_NAME)

class SimpleToolSuite(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        self.config_path = get_default_config_path()
        self.config = self.load_config()

        uic.loadUi('pyqt_simpletoolsuite_2.ui', self)

        self.plugin_manager = PluginManager(self.config.get('plugin_location', os.path.join(os.getcwd(), "plugins")))

        self.download_mode = False

        self.init_ui_components()
        self.connect_signals()
        self.apply_config()
        self.setup_ui()

    def init_ui_components(self):
            """Initialize UI components."""
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
            """Connect UI signals to their respective slots."""
            self.load_button.clicked.connect(self.reset_plugin_list)
            self.launch_button.clicked.connect(self.handle_launch_or_download)
            self.download_button.clicked.connect(self.handle_download_mode)
            self.plugin_list.itemClicked.connect(self.show_metadata)
            self.button_plugin_loc.clicked.connect(self.browse_plugin_location)
            self.button_open_plugin.clicked.connect(self.open_plugin_location)  # Connection here
            self.button_save_settings.clicked.connect(self.save_config_and_plugins)
            self.checkbox_darkmode.stateChanged.connect(self.toggle_dark_mode)
            self.button_open_config.clicked.connect(self.open_config_location)



    def load_config(self):
        """Load the configuration from a file, creating defaults if necessary."""
        config_dir = os.path.dirname(self.config_path)
        if not os.path.exists(config_dir):
            os.makedirs(config_dir)

        if not os.path.exists(self.config_path):
            default_config = {
                "dark_mode": False,
                "plugin_location": os.path.join(os.getcwd(), "plugins")
            }
            with open(self.config_path, 'w') as f:
                json.dump(default_config, f, indent=4)
            return default_config

        with open(self.config_path, 'r') as f:
            return json.load(f)

    def save_config(self):
        """Save the current configuration to the default path."""
        with open(self.config_path, 'w') as f:
            json.dump(self.config, f, indent=4)

    def apply_config(self):
        """Apply the loaded configuration settings to the UI."""
        self.line_edit_plugin_loc.setText(self.config.get('plugin_location', os.path.join(os.getcwd(), "plugins")))
        dark_mode_enabled = self.config.get('dark_mode', False)
        self.checkbox_darkmode.setChecked(dark_mode_enabled)
        self.apply_style(dark_mode_enabled)

    def apply_style(self, dark_mode_enabled):
        """Apply the appropriate stylesheet based on dark mode setting."""
        style_sheet = DARK_MODE_STYLE if dark_mode_enabled else "light_mode.css"
        if os.path.exists(style_sheet):
            try:
                with open(style_sheet, "r") as file:
                    style_content = file.read()
                    self.setStyleSheet(style_content)
            except Exception as e:
                print(f"Error applying stylesheet: {e}")
        else:
            print(f"{style_sheet} CSS file not found.")

    def setup_ui(self):
        """Initial UI setup."""
        self.populate_plugins()
        self.tab_widget.setTabText(0, "Plugins")  # Ensure Tab 1 name is set
        self.tab_widget.setTabText(1, "Settings")  # Ensure Tab 2 name is set
        self.tab_widget.setTabsClosable(True)

        # Hide close buttons on desired tabs (plugins and settings)
        self.tab_widget.tabBar().setTabButton(0, QtWidgets.QTabBar.RightSide, None)
        self.tab_widget.tabBar().setTabButton(1, QtWidgets.QTabBar.RightSide, None)
        self.tab_widget.setCurrentIndex(0) #Set Plugins Tab as the active tab on startup.
        self.tab_widget.setTabVisible(2, False)# Ensure the plugin execution tab is initially hidden
        self.tab_widget.tabCloseRequested.connect(self.handle_tab_close)
        self.load_button.clicked.connect(self.reset_plugin_list)
        self.launch_button.clicked.connect(self.launch_plugin)
        self.download_button.clicked.connect(self.handle_download_mode)



    def populate_plugins(self):
        """Populate the plugin list with installed plugins."""
        plugins = self.plugin_manager.discover_plugins()
        self.plugin_list.clear()
        for plugin in plugins:
            self.plugin_list.addItem(plugin["name"])

    def reset_plugin_list(self):
        """Reset to show user-installed plugins."""
        self.download_mode = False
        self.label_plugin_mode.setText("Your Plugins:")
        self.populate_plugins()
        self.launch_button.setText("Launch Plugin")

    def open_plugin_location(self):
            """Open the directory specified in the plugin location line edit."""
            dir_ = self.line_edit_plugin_loc.text().strip()  # Get the directory path from the line edit
            if os.path.exists(dir_):
                QtGui.QDesktopServices.openUrl(QtCore.QUrl.fromLocalFile(dir_))
            else:
                QtWidgets.QMessageBox.warning(self, "Invalid Directory", "The specified directory does not exist.")

    def open_config_location(self):
            """Open the directory where the config file is located."""
            config_dir = os.path.dirname(self.config_path)  # Get the directory of config path
            if os.path.exists(config_dir):
                QtGui.QDesktopServices.openUrl(QtCore.QUrl.fromLocalFile(config_dir))
            else:
                QtWidgets.QMessageBox.warning(self, "Directory Not Found", "The configuration directory does not exist.")

    def handle_download_mode(self):
        """Enter download mode to show available plugins."""
        if not self.download_mode:
            self.enter_download_mode()

    def enter_download_mode(self):
        """Set the UI to download mode."""
        self.download_mode = True
        self.label_plugin_mode.setText("Download Plugin:")
        self.launch_button.setText("Download Plugin")
        self.fetch_available_plugins()

    def fetch_available_plugins(self):
        """Fetch the list of available plugins and their metadata from the GitHub repository."""
        try:
            response = requests.get(GITHUB_API_URL)
            if response.status_code == 200:
                available_entries = response.json()
                self.available_plugins = {}

                for entry in available_entries:
                    if entry["type"] == "dir":
                        plugin_name = entry["name"]
                        metadata_url = f"https://raw.githubusercontent.com/MaxTheSpy/SimpleToolSuite/main/Available%20Plugins/{plugin_name}/metadata.json"
                        metadata_response = requests.get(metadata_url)
                        if metadata_response.status_code == 200:
                            # Parse the metadata.json fetched from the URL correctly
                            metadata_content = metadata_response.json()
                            self.available_plugins[plugin_name] = metadata_content
                        else:
                            print(f"Failed to fetch metadata for {plugin_name}: {metadata_response.status_code}")

                self.plugin_list.clear()
                for plugin_name in self.available_plugins.keys():
                    self.plugin_list.addItem(plugin_name)
            else:
                self.description_list.addItem(f"Failed to fetch plugins: {response.status_code}")
        except Exception as e:
            self.description_list.addItem(f"Error fetching plugins: {e}")

    def show_metadata(self, item):
        """Display metadata content for the selected plugin, either installed or downloadable."""
        self.description_list.clear()
        plugin_name = item.text()
        print(f"Selected plugin: {plugin_name}")

        metadata = None

        if self.download_mode:
            # Fetch from available_plugins dictionary if in download mode
            metadata = self.available_plugins.get(plugin_name)
        else:
            # Fetch metadata for installed plugins
            plugins = self.plugin_manager.discover_plugins()
            selected_plugin = next((p for p in plugins if p["name"] == plugin_name), None)

            if selected_plugin:
                metadata_path = os.path.join(selected_plugin["path"], "metadata.json")
                if os.path.exists(metadata_path):
                    with open(metadata_path, "r") as meta_file:
                        metadata = json.load(meta_file)

        # Define which metadata fields to display and their labels
        fields_to_display = {
            "name": "Name",
            "version": "Version",
            "author": "Author",
            "description": "Description"
        }

        if metadata and isinstance(metadata, dict):
            for key, display_name in fields_to_display.items():
                if key in metadata:
                    value = metadata[key]
                    self.description_list.addItem(f"{display_name}: {value}")  # Capitalized labels

            # Display features if they exist
            if "features" in metadata:
                self.description_list.addItem("")  # Add an empty line for spacing
                self.description_list.addItem("Features:")  # Features header
                for feature in metadata["features"]:
                    self.description_list.addItem(f"  - {feature}")  # List each feature with a bullet point
            else:
                self.description_list.addItem("No metadata available or improperly formatted.")

    def handle_launch_or_download(self):
        """Launch the selected plugin or download depending on the mode."""
        if self.download_mode:
            self.download_selected_plugin()
        else:
            self.launch_plugin()

    def download_selected_plugin(self):
        """Download the selected plugin."""
        selected_item = self.plugin_list.currentItem()
        if not selected_item:
            self.description_list.addItem("No plugin selected.")
            return

        plugin_name = selected_item.text()
        success = self.plugin_manager.download_plugin(GITHUB_API_URL, plugin_name)
        message = f"Plugin '{plugin_name}' installed successfully." if success else f"Failed to download plugin '{plugin_name}'."
        self.description_list.addItem(message)
        if success:
            self.reset_plugin_list()

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


    def browse_plugin_location(self):
        """Open a dialog to select a new plugin directory."""
        dir_ = QtWidgets.QFileDialog.getExistingDirectory(self, "Select Plugin Directory", self.line_edit_plugin_loc.text() or os.getcwd())
        if dir_:
            self.line_edit_plugin_loc.setText(dir_)
            self.config['plugin_location'] = dir_

    def save_config_and_plugins(self):
        """Save configuration and relocate plugins if necessary."""
        new_plugin_location = self.line_edit_plugin_loc.text().strip()
        if new_plugin_location and os.path.exists(new_plugin_location):
            self.move_plugins(new_plugin_location)
            self.plugin_manager.plugin_dir = new_plugin_location

        self.config['plugin_location'] = new_plugin_location
        self.save_config()
        self.populate_plugins()

    def move_plugins(self, new_plugin_location):
        """Move plugins to a new directory location."""
        current_plugin_location = self.plugin_manager.plugin_dir
        if os.path.exists(current_plugin_location):
            for plugin in os.listdir(current_plugin_location):
                plugin_path = os.path.join(current_plugin_location, plugin)
                new_path = os.path.join(new_plugin_location, plugin)
                if os.path.isdir(plugin_path):
                    try:
                        shutil.move(plugin_path, new_path)
                        print(f"Moved {plugin} to new location.")
                    except Exception as e:
                        print(f"Failed to move {plugin}: {e}")

    def toggle_dark_mode(self, state):
        """Toggle the application's dark mode setting."""
        enabled = state == QtCore.Qt.Checked
        self.config['dark_mode'] = enabled
        self.save_config()
        self.apply_style(enabled)


if __name__ == "__main__":
    app = QtWidgets.QApplication([])
    window = SimpleToolSuite()
    window.show()
    app.exec_()
