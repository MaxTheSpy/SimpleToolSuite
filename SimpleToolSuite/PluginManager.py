from PyQt5 import QtWidgets, uic
from pluginmanager import PluginManager  # Import your PluginManager class

class SimpleToolSuite(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        uic.loadUi('pyqt_simpletoolsuite_1.ui', self)

        # Access widgets
        self.plugin_list = self.findChild(QtWidgets.QListWidget, "listWidget")
        self.metadata_box = self.findChild(QtWidgets.QTextEdit, "textEdit")
        self.load_button = self.findChild(QtWidgets.QPushButton, "button_load_plugin")
        self.launch_button = self.findChild(QtWidgets.QPushButton, "button_launch_plugin")
        self.download_button = self.findChild(QtWidgets.QPushButton, "button_download_plugin")

        # Initialize PluginManager
        self.plugin_manager = PluginManager(plugin_dir="plugins")

        # Populate plugins and set up connections
        self.populate_plugins()
        self.plugin_list.itemClicked.connect(self.show_metadata)
        self.load_button.clicked.connect(self.load_plugins)
        self.launch_button.clicked.connect(self.launch_plugin)
        self.download_button.clicked.connect(self.download_plugin)

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
            else:
                self.metadata_box.setText("Metadata file not found.")
        else:
            self.metadata_box.setText("Plugin not found.")

    def load_plugins(self):
        """Refresh the plugin list."""
        self.populate_plugins()

    def launch_plugin(self):
        """Launch the selected plugin."""
        selected_item = self.plugin_list.currentItem()
        if not selected_item:
            self.metadata_box.setText("No plugin selected.")
            return

        plugin_name = selected_item.text()
        plugins = self.plugin_manager.discover_plugins()
        selected_plugin = next((p for p in plugins if p["name"] == plugin_name), None)

        if selected_plugin:
            module = self.plugin_manager.load_plugin(selected_plugin["path"], selected_plugin["main"])
            if hasattr(module, "main"):
                # Load the plugin's UI or functionality
                module.main()
            else:
                self.metadata_box.setText("Plugin does not have a main function.")
        else:
            self.metadata_box.setText("Plugin not found.")

    def download_plugin(self):
        """Download a plugin from the repository."""
        # Prompt the user for the plugin name
        plugin_name, ok = QtWidgets.QInputDialog.getText(self, "Download Plugin", "Enter the plugin name:")
        if not ok or not plugin_name.strip():
            return  # User canceled or entered an invalid name

        # Repository URL
        repo_url = "https://api.github.com/repos/MaxTheSpy/SimpleToolSuite/contents/SimpleToolSuite/plugins"

        # Download the plugin
        success = self.plugin_manager.download_plugin(repo_url, plugin_name.strip())
        if success:
            QtWidgets.QMessageBox.information(self, "Success", f"Plugin '{plugin_name}' downloaded successfully.")
            self.populate_plugins()  # Refresh the plugin list
        else:
            QtWidgets.QMessageBox.critical(self, "Error", f"Failed to download plugin '{plugin_name}'.")
