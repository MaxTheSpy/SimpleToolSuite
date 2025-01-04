import os
import importlib
import json
import subprocess

class PluginManager:
    def __init__(self, plugin_dir="plugins"):
        self.plugin_dir = plugin_dir

    def discover_plugins(self):
        """Discover all plugins in the plugin directory."""
        plugins = []
        for plugin_name in os.listdir(self.plugin_dir):
            plugin_path = os.path.join(self.plugin_dir, plugin_name)
            metadata_file = os.path.join(plugin_path, "metadata.json")
            if os.path.isdir(plugin_path) and os.path.isfile(metadata_file):
                with open(metadata_file, "r") as f:
                    metadata = json.load(f)
                    metadata["path"] = plugin_path
                    plugins.append(metadata)
        return plugins

    def install_dependencies(self, plugin_metadata):
        """Install dependencies for a plugin."""
        requirements_file = os.path.join(plugin_metadata["path"], "requirements.txt")
        if os.path.isfile(requirements_file):
            subprocess.run(["pip", "install", "-r", requirements_file], check=True)

    def run_plugin(self, plugin_metadata):
        """Run a plugin by importing its main module."""
        entry_point = plugin_metadata["entry_point"]
        plugin_path = plugin_metadata["path"]
        module_name = os.path.splitext(entry_point)[0]
        spec = importlib.util.spec_from_file_location(module_name, os.path.join(plugin_path, entry_point))
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        if hasattr(module, "main"):
            module.main()
