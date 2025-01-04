import os
import importlib.util
import tkinter as tk
from tkinter import simpledialog
from tkinter import ttk, messagebox, filedialog
import json
import requests

plugin_alias = {
    "SMGA": "SimpleMusicGenreAnalyzer",
    # Add more aliases here
}

class PluginManager:
    def __init__(self, plugin_dir="plugins"):
        self.plugin_dir = plugin_dir

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
                                "alias": metadata.get("alias", folder),
                                "path": plugin_path,
                                "main": metadata.get("main", "main.py"),
                            })
                        except json.JSONDecodeError:
                            print(f"Invalid metadata.json in {folder}")
        return plugins

    def load_plugin(self, plugin_path, main_file):
        main_file_path = os.path.join(plugin_path, main_file)
        if os.path.exists(main_file_path):
            spec = importlib.util.spec_from_file_location("plugin_main", main_file_path)
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            return module
        return None

    def download_plugin(self, repo_url, plugin_name):
        """Simulates downloading a plugin from a repository."""
        # Replace with real download logic if necessary
        print(f"Simulated download for {plugin_name} from {repo_url}")


def create_ui():
    root = tk.Tk()
    root.title("Simple Tool Suite")

    plugin_manager = PluginManager()

    # UI Elements
    frame = ttk.Frame(root)
    frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

    plugins_listbox = tk.Listbox(frame, height=10, width=50)
    plugins_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5, pady=5)

    scrollbar = ttk.Scrollbar(frame, orient=tk.VERTICAL, command=plugins_listbox.yview)
    scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
    plugins_listbox.config(yscrollcommand=scrollbar.set)

    def load_plugins():
        plugins = plugin_manager.discover_plugins()
        plugins_listbox.delete(0, tk.END)
        for plugin in plugins:
            display_name = f"{plugin['name']} ({plugin.get('alias', '')})"
            plugins_listbox.insert(tk.END, display_name)

    def launch_plugin():
        selected_idx = plugins_listbox.curselection()
        if not selected_idx:
            messagebox.showerror("Error", "No plugin selected")
            return

        plugin_name = plugins_listbox.get(selected_idx).split(" (")[0]  # Extract the name
        plugins = plugin_manager.discover_plugins()
        selected_plugin = next((p for p in plugins if p["name"] == plugin_name or p["alias"] == plugin_name), None)

        if selected_plugin:
            module = plugin_manager.load_plugin(selected_plugin["path"], selected_plugin["main"])
            if hasattr(module, "main"):
                module.main(frame)  # Pass the frame as the parent
            else:
                messagebox.showerror("Error", "Plugin does not have a main function")

    def download_plugin():
        repo_url = "https://api.github.com/repos/MaxTheSpy/SimpleToolSuite/contents/SimpleToolSuiteV1.0.1/plugins"
        plugin_name = simpledialog.askstring("Download Plugin", "Enter the plugin name or alias:")
        if not plugin_name:
            return

        # Resolve the plugin alias
        plugin_name = plugin_alias.get(plugin_name, plugin_name)

        # Build the URL for the plugin directory
        plugin_url = f"{repo_url}/{plugin_name}"
        print(f"Fetching plugin from: {plugin_url}")

        # Make the request to the GitHub API
        response = requests.get(plugin_url)
        if response.status_code != 200:
            print(f"Failed to fetch plugin. Status code: {response.status_code}")
            print(f"Response: {response.text}")
            messagebox.showerror("Error", f"Failed to fetch plugin '{plugin_name}'.")
            return

        try:
            plugin_files = response.json()
            if not isinstance(plugin_files, list):
                print("Unexpected response format from GitHub API.")
                messagebox.showerror("Error", "Unexpected response format from GitHub.")
                return
        except json.JSONDecodeError:
            print("Failed to decode JSON response.")
            messagebox.showerror("Error", "Failed to decode response from GitHub.")
            return

        # Create the plugin directory locally
        plugin_dir = os.path.join(plugin_manager.plugin_dir, plugin_name)
        os.makedirs(plugin_dir, exist_ok=True)

        # Download each file in the plugin directory
        for file in plugin_files:
            if file['type'] == 'file':
                file_url = file['download_url']
                file_path = os.path.join(plugin_dir, file['name'])
                file_response = requests.get(file_url)
                if file_response.status_code == 200:
                    with open(file_path, 'wb') as f:
                        f.write(file_response.content)
                    print(f"Downloaded file: {file['name']}")
                else:
                    print(f"Failed to download file: {file['name']}. Status: {file_response.status_code}")
            elif file['type'] == 'dir':
                print(f"Skipping subdirectory: {file['name']} (not supported yet)")

        messagebox.showinfo("Success", f"Plugin '{plugin_name}' downloaded successfully.")



    # Buttons
    button_frame = ttk.Frame(root)
    button_frame.pack(fill=tk.X, pady=10)

    load_button = ttk.Button(button_frame, text="Load Plugins", command=load_plugins)
    load_button.pack(side=tk.LEFT, padx=5)

    launch_button = ttk.Button(button_frame, text="Launch Plugin", command=launch_plugin)
    launch_button.pack(side=tk.LEFT, padx=5)

    download_button = ttk.Button(button_frame, text="Download Plugin", command=download_plugin)
    download_button.pack(side=tk.LEFT, padx=5)

    # Auto-load plugins at startup
    load_plugins()

    root.mainloop()

if __name__ == "__main__":
    create_ui()
