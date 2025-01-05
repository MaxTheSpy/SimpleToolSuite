import warnings

warnings.filterwarnings("ignore", category=DeprecationWarning)

import requests
from PyQt5 import QtWidgets, uic
import os
import json
import importlib.util


VERSION = "1.0.3"
GITHUB_API_URL = "https://api.github.com/repos/MaxTheSpy/SimpleToolSuite/contents/Available%20Plugins"


class PluginManager:
    def __init__(self, plugin_dir="plugins"):
        self.plugin_dir = plugin_dir

    def discover_plugins(self):
        """Discover installed plugins."""
        plugins = []
        if not os.path.exists(self.plugin_dir):
            os.makedirs(self.plugin_dir)

        for folder in os.listdir(self.plugin_dir):
            plugin_path = os.path.join(self.plugin_dir, folder)
            if os.path.isdir(plugin_path):
                metadata_path = os.path.join(plugin_path, "metadata.json")
                if os.path.exists(metadata_path):
                    with open(metadata_path, "r") as meta_file:
                        try:
                            metadata = json.load(meta_file)
                            plugins.append({
                                "name": metadata.get("name", folder),
                                "alias": metadata.get("alias", folder),
                                "path": plugin_path,
                                "main": metadata.get("main", "main.py"),
                                "version": metadata.get("version", "N/A"),
                                "description": metadata.get("description", "No description available."),
                            })
                        except json.JSONDecodeError:
                            print(f"Invalid metadata.json in {folder}")
        return plugins

    def load_plugin(self, plugin_path, main_file):
        """Load a plugin by importing its main module."""
        main_file_path = os.path.join(plugin_path, main_file)
        if os.path.exists(main_file_path):
            spec = importlib.util.spec_from_file_location("plugin_main", main_file_path)
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            return module
        return None


class SimpleToolSuite(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        # Load the main UI
        uic.loadUi('pyqt_simpletoolsuite_1.ui', self)

        # Access widgets
        self.tab_widget = self.findChild(QtWidgets.QTabWidget, "tabWidget")
        self.plugin_list = self.findChild(QtWidgets.QListWidget, "listWidget")
        self.metadata_box = self.findChild(QtWidgets.QTextEdit, "textEdit")
        self.load_button = self.findChild(QtWidgets.QPushButton, "button_load_plugin")
        self.launch_button = self.findChild(QtWidgets.QPushButton, "button_launch_plugin")
        self.download_button = self.findChild(QtWidgets.QPushButton, "button_download_plugin")

        # Initialize PluginManager
        self.plugin_manager = PluginManager(plugin_dir="plugins")

        # Flags
        self.download_mode = False

        # Setup UI
        self.setup_ui()

    def setup_ui(self):
        """Initial UI setup."""
        self.populate_plugins()
        self.tab_widget.setTabText(0, "Plugin List")  # Set Tab 1 name
        self.tab_widget.setTabsClosable(True)  # Enable closable tabs
        self.tab_widget.tabCloseRequested.connect(self.close_tab)  # Connect tab close signal
        self.tab_widget.tabBar().setTabButton(0, QtWidgets.QTabBar.RightSide, None)  # Disable close button for Tab 0
        self.tab_widget.setTabVisible(1, False)  # Ensure Tab 2 is hidden on app launch

        # Set default text for the download button
        self.download_button.setText("Available Plugins")

        # Connect buttons
        self.load_button.clicked.connect(self.reset_plugin_list)
        self.launch_button.clicked.connect(self.launch_plugin)
        self.download_button.clicked.connect(self.handle_download_button)
        self.plugin_list.itemClicked.connect(self.show_metadata)

    def populate_plugins(self):
        """Populate the plugin list with installed plugins."""
        plugins = self.plugin_manager.discover_plugins()
        self.plugin_list.clear()
        for plugin in plugins:
            self.plugin_list.addItem(plugin["name"])

    def reset_plugin_list(self):
        """Reset the plugin list and download button."""
        self.download_mode = False
        self.download_button.setText("Download Plugin")
        self.populate_plugins()

    def show_metadata(self, item):
        """Display metadata for the selected plugin or available plugin."""
        plugin_name = item.text()
        if self.download_mode:
            # Fetch metadata for available plugins
            plugin = self.available_plugins.get(plugin_name, {})
            metadata_text = (
                f"Name: {plugin.get('name', 'Unknown')}\n"
                f"Alias: {plugin.get('alias', 'N/A')}\n"
                f"Version: {plugin.get('version', 'N/A')}\n"
                f"Description: {plugin.get('description', 'No description available.')}\n"
            )
        else:
            # Fetch metadata for installed plugins
            plugins = self.plugin_manager.discover_plugins()
            selected_plugin = next((p for p in plugins if p["name"] == plugin_name), None)
            metadata_text = "Plugin not found." if not selected_plugin else (
                f"Name: {selected_plugin['name']}\n"
                f"Alias: {selected_plugin['alias']}\n"
                f"Version: {selected_plugin['version']}\n"
                f"Description: {selected_plugin['description']}\n"
            )
        self.metadata_box.setText(metadata_text)

    def handle_download_button(self):
        """Handle the click event for the download button."""
        if not self.download_mode:
            self.enter_download_mode()
        else:
            self.download_selected_plugin()

    def enter_download_mode(self):
        """Switch to download mode and fetch available plugins."""
        self.download_mode = True
        self.download_button.setText("Download Selected")
        self.fetch_available_plugins()

    def fetch_available_plugins(self):
        """Fetch the list of available plugins from the GitHub repository."""
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
                            metadata = json.loads(metadata_response.text)
                            self.available_plugins[plugin_name] = metadata

                self.plugin_list.clear()
                for plugin_name in self.available_plugins.keys():
                    self.plugin_list.addItem(plugin_name)
            else:
                self.metadata_box.setText(f"Failed to fetch plugins: {response.status_code}")
        except Exception as e:
            self.metadata_box.setText(f"Error fetching plugins: {e}")

    def download_selected_plugin(self):
        """Download and install the selected plugin."""
        selected_item = self.plugin_list.currentItem()
        if not selected_item:
            self.metadata_box.setText("No plugin selected.")
            return

        plugin_name = selected_item.text()
        plugin_url = f"{GITHUB_API_URL}/{plugin_name}"
        try:
            response = requests.get(plugin_url)
            if response.status_code == 200:
                plugin_dir = os.path.join(self.plugin_manager.plugin_dir, plugin_name)
                os.makedirs(plugin_dir, exist_ok=True)
                for entry in response.json():
                    if entry["type"] == "file":
                        file_url = entry["download_url"]
                        file_response = requests.get(file_url)
                        if file_response.status_code == 200:
                            file_path = os.path.join(plugin_dir, entry["name"])
                            with open(file_path, "wb") as file:
                                file.write(file_response.content)
                self.metadata_box.setText(f"Plugin '{plugin_name}' installed successfully.")
                self.reset_plugin_list()
            else:
                self.metadata_box.setText(f"Failed to download plugin: {response.status_code}")
        except Exception as e:
            self.metadata_box.setText(f"Error downloading plugin: {e}")

    def launch_plugin(self):
        """Launch the selected plugin."""
        selected_item = self.plugin_list.currentItem()
        if not selected_item:
            self.metadata_box.setText("No plugin selected.")
            return

        plugin_name = selected_item.text()
        plugins = self.plugin_manager.discover_plugins()
        selected_plugin = next((p for p in plugins if p["name"] == plugin_name), None)
        if not selected_plugin:
            self.metadata_box.setText("Plugin not found.")
            return

        try:
            module = self.plugin_manager.load_plugin(selected_plugin["path"], selected_plugin["main"])
            if hasattr(module, "main"):
                # Clear Tab 2 content completely
                scroll_area = self.findChild(QtWidgets.QScrollArea, "scroll_plugin_container")
                if scroll_area:
                    scroll_area_widget = scroll_area.findChild(QtWidgets.QWidget, "scrollAreaWidgetContents")
                    if scroll_area_widget:
                        # Remove and recreate the scroll area widget
                        layout = scroll_area_widget.layout()
                        if layout:
                            self.clear_layout(layout)  # Clear existing layout

                        # Recreate the widget and reset the layout
                        new_scroll_area_widget = QtWidgets.QWidget(scroll_area)
                        new_scroll_area_widget.setObjectName("scrollAreaWidgetContents")
                        new_scroll_area_widget.setLayout(QtWidgets.QVBoxLayout())
                        scroll_area.setWidget(new_scroll_area_widget)

                        # Load and launch the plugin
                        module.main(new_scroll_area_widget)

                        # Update Tab 2 properties and show it
                        self.tab_widget.setTabText(1, plugin_name)
                        self.tab_widget.setTabVisible(1, True)
                        self.tab_widget.setCurrentIndex(1)
            else:
                self.metadata_box.setText("Plugin does not have a main function.")
        except Exception as e:
            self.metadata_box.setText(f"Failed to load plugin: {e}")

    def clear_layout(self, layout):
        """Recursively clear all items in a layout."""
        while layout.count():
            child = layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()
            elif child.layout():
                self.clear_layout(child.layout())

    def close_tab(self, index):
        """Hide Tab 2 and clear its content."""
        if index != 0:  # Prevent closing the main Plugin List tab
            scroll_area = self.findChild(QtWidgets.QScrollArea, "scroll_plugin_container")
            if scroll_area:
                scroll_area_widget = scroll_area.findChild(QtWidgets.QWidget, "scrollAreaWidgetContents")
                if scroll_area_widget:
                    # Clear all widgets inside the scroll area
                    layout = scroll_area_widget.layout()
                    if layout:
                        self.clear_layout(layout)

            # Hide Tab 2
            self.tab_widget.setTabVisible(1, False)

if __name__ == "__main__":
    app = QtWidgets.QApplication([])
    window = SimpleToolSuite()
    window.show()
    app.exec_()
