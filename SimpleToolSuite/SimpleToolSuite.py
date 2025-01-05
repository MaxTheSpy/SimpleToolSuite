from PyQt5 import QtWidgets, uic
import os
import json
import importlib.util
import warnings

warnings.filterwarnings("ignore", category=DeprecationWarning)

VERSION = "1.0.3"


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

        # Initialize PluginManager
        self.plugin_manager = PluginManager(plugin_dir="plugins")

        # Setup UI
        self.setup_ui()

    def setup_ui(self):
        """Initial UI setup."""
        self.populate_plugins()
        self.tab_widget.setTabText(0, "Plugin List")  # Set Tab 1 name
        self.tab_widget.setTabVisible(1, False)  # Hide Tab 2 initially

        # Connect buttons
        self.load_button.clicked.connect(self.populate_plugins)
        self.launch_button.clicked.connect(self.launch_plugin)
        self.plugin_list.itemClicked.connect(self.show_metadata)  # Connect item click to show_metadata

    def populate_plugins(self):
        """Populate the plugin list."""
        plugins = self.plugin_manager.discover_plugins()
        self.plugin_list.clear()
        for plugin in plugins:
            self.plugin_list.addItem(plugin["name"])

    def show_metadata(self, item):
        """Display metadata for the selected plugin."""
        plugin_name = item.text()
        plugins = self.plugin_manager.discover_plugins()
        selected_plugin = next((p for p in plugins if p["name"] == plugin_name), None)

        if selected_plugin:
            metadata_path = os.path.join(selected_plugin["path"], "metadata.json")
            if os.path.exists(metadata_path):
                try:
                    with open(metadata_path, "r") as meta_file:
                        metadata = json.load(meta_file)
                        metadata_text = (
                            f"Name: {metadata.get('name', 'Unknown')}\n"
                            f"Alias: {metadata.get('alias', 'N/A')}\n"
                            f"Version: {metadata.get('version', 'N/A')}\n"
                            f"Main File: {metadata.get('main', 'N/A')}\n"
                            f"Description: {metadata.get('description', 'No description available.')}\n"
                        )
                        self.metadata_box.setText(metadata_text)
                except json.JSONDecodeError:
                    self.metadata_box.setText(f"Error reading metadata for {plugin_name}.")
            else:
                self.metadata_box.setText("Metadata file not found.")
        else:
            self.metadata_box.setText("Plugin not found.")

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

        # Access the QScrollArea and its widget
        scroll_area = self.findChild(QtWidgets.QScrollArea, "scroll_plugin_container")
        if not scroll_area:
            self.metadata_box.setText("Scroll area not found.")
            return

        scroll_area_widget = scroll_area.findChild(QtWidgets.QWidget, "scrollAreaWidgetContents")
        if not scroll_area_widget:
            self.metadata_box.setText("Scroll area contents not found.")
            return

        # Clear the existing layout in the scroll area
        if scroll_area_widget.layout() is None:
            scroll_area_widget.setLayout(QtWidgets.QVBoxLayout())
        else:
            for i in reversed(range(scroll_area_widget.layout().count())):
                widget_to_remove = scroll_area_widget.layout().itemAt(i).widget()
                scroll_area_widget.layout().removeWidget(widget_to_remove)
                widget_to_remove.deleteLater()

        # Load and run the plugin
        try:
            print(f"[DEBUG] Loading plugin: {plugin_name}")  # Debug log
            module = self.plugin_manager.load_plugin(selected_plugin["path"], selected_plugin["main"])
            if hasattr(module, "main"):
                module.main(scroll_area_widget)  # Pass the widget inside the scroll area
                self.tab_widget.setTabText(1, plugin_name)  # Rename Tab 2
                self.tab_widget.setTabVisible(1, True)  # Show Tab 2
                self.tab_widget.setCurrentIndex(1)  # Switch to Tab 2
            else:
                self.metadata_box.setText("Plugin does not have a main function.")
        except Exception as e:
            print(f"[ERROR] Failed to load plugin: {e}")  # Debug log
            self.metadata_box.setText(f"Failed to load plugin: {e}")


if __name__ == "__main__":
    app = QtWidgets.QApplication([])
    window = SimpleToolSuite()
    window.show()
    app.exec_()
