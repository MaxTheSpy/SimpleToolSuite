import os
import importlib.util
import json
import subprocess
import requests
import zipfile

class PluginManager:
    def __init__(self, plugin_dir="plugins"):
        self.plugin_dir = plugin_dir

    def discover_plugins(self):
        """Discover available plugins and their metadata."""
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
            try:
                subprocess.run(["pip", "install", "-r", requirements_file], check=True)
            except subprocess.CalledProcessError as e:
                print(f"Failed to install dependencies for {plugin_metadata['name']}: {e}")

    def run_plugin(self, plugin_metadata, parent=None):
        """Run a plugin by loading and executing its main module."""
        main_file = plugin_metadata.get("main")
        if not main_file:
            print(f"No main file specified for plugin: {plugin_metadata['name']}")
            return

        main_file_path = os.path.join(plugin_metadata["path"], main_file)
        if not os.path.exists(main_file_path):
            print(f"Main file not found for plugin: {plugin_metadata['name']}")
            return

        spec = importlib.util.spec_from_file_location("plugin_main", main_file_path)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        if hasattr(module, "main"):
            # Pass parent if provided for embedding UI in a parent frame
            if parent:
                module.main(parent)
            else:
                module.main()
        else:
            print(f"Plugin {plugin_metadata['name']} does not have a main() function.")

    def download_plugin(self, repo_url, plugin_name):
        """Download and extract a plugin from a repository."""
        try:
            plugin_url = f"{repo_url}/{plugin_name}/archive/refs/heads/main.zip"
            response = requests.get(plugin_url, stream=True)
            if response.status_code == 200:
                zip_path = os.path.join(self.plugin_dir, f"{plugin_name}.zip")
                with open(zip_path, "wb") as file:
                    for chunk in response.iter_content(chunk_size=1024):
                        file.write(chunk)

                # Extract the plugin
                with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                    zip_ref.extractall(self.plugin_dir)

                # Remove the zip file after extraction
                os.remove(zip_path)

                print(f"Plugin {plugin_name} downloaded and extracted successfully.")
                return True
            else:
                print(f"Failed to download plugin: {response.status_code}")
                return False
        except Exception as e:
            print(f"Error downloading plugin {plugin_name}: {e}")
            return False
