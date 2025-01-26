import os
import json
import requests
import sys

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
        """Load the main module of a plugin."""
        try:
            # Activate the plugin's virtual environment before loading
            self.load_plugin_dependencies(plugin_path)

            main_module = os.path.splitext(main_file)[0]
            module_path = os.path.join(plugin_path, main_file)
            print(f"Attempting to load module: {module_path}")

            if os.path.exists(module_path):
                import importlib.util
                spec = importlib.util.spec_from_file_location(main_module, module_path)
                module = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(module)
                print(f"Module loaded: {module}")
                return module
            else:
                print(f"Main file not found at: {module_path}")
        except Exception as e:
            print(f"Failed to load plugin: {e}")
        return None

    def load_plugin_dependencies(self, plugin_path):
        """
        Activates the virtual environment for the specified plugin and ensures its site-packages is added to sys.path.
        """
        venv_path = os.path.join(plugin_path, ".venv", "bin", "activate_this.py")
        venv_lib_site_packages = os.path.join(plugin_path, ".venv", "lib", "python3.12", "site-packages")
        venv_lib64_site_packages = os.path.join(plugin_path, ".venv", "lib64", "python3.12", "site-packages")

        if os.path.exists(venv_path):
            try:
                print(f"Activating virtual environment: {venv_path}")
                exec(open(venv_path).read(), {'__file__': venv_path})
                print(f"Virtual environment activated for plugin: {plugin_path}")

                # Add lib/site-packages to sys.path if it exists and is not already present
                if os.path.exists(venv_lib_site_packages) and venv_lib_site_packages not in sys.path:
                    print(f"Adding lib site-packages to sys.path: {venv_lib_site_packages}")
                    sys.path.insert(0, venv_lib_site_packages)

                # Add lib64/site-packages to sys.path if it exists and is not already present
                if os.path.exists(venv_lib64_site_packages) and venv_lib64_site_packages not in sys.path:
                    print(f"Adding lib64 site-packages to sys.path: {venv_lib64_site_packages}")
                    sys.path.insert(0, venv_lib64_site_packages)

            except Exception as e:
                print(f"Failed to activate virtual environment for plugin: {plugin_path}. Error: {e}")
        else:
            print(f"Virtual environment not found at: {venv_path}")

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
