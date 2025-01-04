import os
import importlib
import json
import subprocess

def discover_plugins(self):
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
                            "alias": metadata.get("alias", ""),
                            "path": plugin_path,
                            "main": metadata.get("main", "main.py")
                        })
                    except json.JSONDecodeError:
                        print(f"Invalid metadata.json in {folder}")
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
