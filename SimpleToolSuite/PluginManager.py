import os
import json
import requests

class PluginManager:
    def __init__(self, plugin_dir):
        self.plugin_dir = plugin_dir

    def discover_plugins(self):
        """Discover available plugins within the designated plugin directory."""
        plugins = []
        if not os.path.exists(self.plugin_dir):
            os.makedirs(self.plugin_dir)

        for folder in os.listdir(self.plugin_dir):
            plugin_path = os.path.join(self.plugin_dir, folder)
            if os.path.isdir(plugin_path):
                metadata_path = os.path.join(plugin_path, "metadata.json")
                if os.path.exists(metadata_path):
                    try:
                        with open(metadata_path, "r") as meta_file:
                            metadata = json.load(meta_file)
                            plugins.append({
                                "name": metadata.get("name", folder),
                                "author": metadata.get("author", "Unknown"),
                                "path": plugin_path,
                                "main": metadata.get("main", "main.py"),
                                "version": metadata.get("version", "N/A"),
                                "description": metadata.get("description", "No description available."),
                            })
                    except json.JSONDecodeError:
                        print(f"Invalid JSON in metadata.json for {folder}")
        return plugins

    def load_plugin(self, plugin_path, main_file):
        """Dynamically load a plugin from the specified path and main file."""
        try:
            main_module = os.path.splitext(main_file)[0]
            module_path = os.path.join(plugin_path, main_file)

            # Import module only if main file exists
            if os.path.exists(module_path):
                import importlib.util
                spec = importlib.util.spec_from_file_location(main_module, module_path)
                module = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(module)
                return module
            else:
                print(f"Main file not found for plugin at {plugin_path}")
        except Exception as e:
            print(f"Failed to load plugin from {plugin_path}: {e}")
        return None

    def download_plugin(self, repo_url, plugin_name):
        """Download a plugin from a given repository URL."""
        plugin_url = f"{repo_url}/{plugin_name}"
        try:
            response = requests.get(plugin_url)
            if response.status_code == 200:
                plugin_dir = os.path.join(self.plugin_dir, plugin_name)
                os.makedirs(plugin_dir, exist_ok=True)
                for entry in response.json():
                    if entry["type"] == "file":
                        file_url = entry["download_url"]
                        file_response = requests.get(file_url)
                        if file_response.status_code == 200:
                            file_path = os.path.join(plugin_dir, entry["name"])
                            with open(file_path, "wb") as file:
                                file.write(file_response.content)
                print(f"Plugin '{plugin_name}' downloaded successfully.")
                return True
            else:
                print(f"Failed to download plugin: {response.status_code}")
        except Exception as e:
            print(f"Error downloading plugin '{plugin_name}': {e}")
        return False
