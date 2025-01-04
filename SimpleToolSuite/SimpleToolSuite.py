import os
import importlib.util
import tkinter as tk
from tkinter import ttk, messagebox
from packaging import version
import json
import requests

# Application version
VERSION = "1.0.2"

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

def download_plugin_window(plugin_manager):
    """Open a new window for plugin download."""
    download_window = tk.Toplevel()
    download_window.title("Download Plugins")
    download_window.geometry("500x400")

    # Frame for plugin list and description
    plugins_frame = ttk.Frame(download_window)
    plugins_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

    plugins_label = ttk.Label(plugins_frame, text="Available Plugins:")
    plugins_label.pack(anchor="w", pady=5)

    plugins_listbox = tk.Listbox(plugins_frame, height=10, width=40)
    plugins_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5, pady=5)

    scrollbar = ttk.Scrollbar(plugins_frame, orient=tk.VERTICAL, command=plugins_listbox.yview)
    scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
    plugins_listbox.config(yscrollcommand=scrollbar.set)

    description_label = ttk.Label(download_window, text="Description:")
    description_label.pack(anchor="w", padx=10, pady=5)

    description_text = tk.Text(download_window, wrap=tk.WORD, height=5, state=tk.DISABLED)
    description_text.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

    def fetch_plugins():
        """Fetch available plugins from GitHub and populate the list."""
        repo_url = "https://api.github.com/repos/MaxTheSpy/SimpleToolSuite/contents/SimpleToolSuite/plugins"
        try:
            response = requests.get(repo_url)
            if response.status_code == 200:
                plugins = response.json()
                plugins_listbox.delete(0, tk.END)
                for plugin in plugins:
                    if plugin["type"] == "dir":
                        plugins_listbox.insert(tk.END, plugin["name"].replace("_", " "))
            else:
                messagebox.showerror("Error", f"Failed to fetch plugin list. Status: {response.status_code}")
        except requests.RequestException as e:
            messagebox.showerror("Error", f"Error connecting to GitHub: {e}")

    def show_description(event):
        """Show the description of the selected plugin."""
        selected_idx = plugins_listbox.curselection()
        if not selected_idx:
            description_text.config(state=tk.NORMAL)
            description_text.delete("1.0", tk.END)
            description_text.insert(tk.END, "No plugin selected.")
            description_text.config(state=tk.DISABLED)
            return

        plugin_name = plugins_listbox.get(selected_idx).replace(" ", "")
        metadata_url = f"https://raw.githubusercontent.com/MaxTheSpy/SimpleToolSuite/main/SimpleToolSuite/plugins/{plugin_name}/metadata.json"
        try:
            response = requests.get(metadata_url)
            if response.status_code == 200:
                metadata = response.json()
                description = (
                    f"Name: {metadata.get('name', 'Unknown')}\n"
                    f"Alias: {metadata.get('alias', 'N/A')}\n"
                    f"Version: {metadata.get('version', 'N/A')}\n"
                    f"Required Version: {metadata.get('required_version', 'N/A')}\n"
                    f"Description: {metadata.get('description', 'No description provided.')}\n"
                )
            else:
                description = "Failed to fetch metadata."
        except requests.RequestException as e:
            description = f"Error fetching metadata: {e}"

        description_text.config(state=tk.NORMAL)
        description_text.delete("1.0", tk.END)
        description_text.insert(tk.END, description)
        description_text.config(state=tk.DISABLED)

    def download_selected_plugin():
        """Download the selected plugin and check version compatibility."""
        selected_idx = plugins_listbox.curselection()
        if not selected_idx:
            messagebox.showerror("Error", "No plugin selected.")
            return

        plugin_name = plugins_listbox.get(selected_idx).replace(" ", "")
        metadata_url = f"https://raw.githubusercontent.com/MaxTheSpy/SimpleToolSuite/main/SimpleToolSuite/plugins/{plugin_name}/metadata.json"

        try:
            response = requests.get(metadata_url)
            if response.status_code != 200:
                raise Exception(f"Failed to fetch metadata for plugin '{plugin_name}'.")

            metadata = response.json()
            required_version = metadata.get("required_version", "0.0.0")
            if version.parse(VERSION) < version.parse(required_version):
                messagebox.showerror(
                    "Version Mismatch",
                    f"Plugin '{plugin_name}' requires SimpleToolSuite v{required_version} or later.\n"
                    f"You are running v{VERSION}. Please update your application."
                )
                return

            download_plugin_files(plugin_name)
        except Exception as e:
            messagebox.showerror("Error", f"An error occurred: {e}")

    def download_plugin_files(plugin_name):
        """Download all files for the plugin."""
        plugin_url = f"https://api.github.com/repos/MaxTheSpy/SimpleToolSuite/contents/SimpleToolSuite/plugins/{plugin_name}"
        response = requests.get(plugin_url)
        if response.status_code != 200:
            messagebox.showerror("Error", f"Failed to fetch plugin: {plugin_name}")
            return

        plugin_files = response.json()
        plugin_dir = os.path.join(plugin_manager.plugin_dir, plugin_name)
        os.makedirs(plugin_dir, exist_ok=True)

        for file in plugin_files:
            if file['type'] == 'file':
                file_url = file['download_url']
                file_path = os.path.join(plugin_dir, file['name'])
                file_response = requests.get(file_url)
                if file_response.status_code == 200:
                    with open(file_path, 'wb') as f:
                        f.write(file_response.content)
                else:
                    print(f"Failed to download {file['name']}.")

        messagebox.showinfo("Success", f"Plugin '{plugin_name}' downloaded successfully.")
        fetch_plugins()

    plugins_listbox.bind("<<ListboxSelect>>", show_description)

        # Buttons for Refresh List and Download Selected
    buttons_frame = ttk.Frame(download_window)
    buttons_frame.pack(fill=tk.X, pady=10)

    ttk.Button(buttons_frame, text="Refresh List", command=fetch_plugins).pack(side=tk.LEFT, padx=5)
    ttk.Button(buttons_frame, text="Download Selected", command=download_selected_plugin).pack(side=tk.LEFT, padx=5)

    fetch_plugins()

def create_ui():
    """Create the main UI for the application."""
    root = tk.Tk()
    root.title(f"Simple Tool Suite v{VERSION}")

    plugin_manager = PluginManager()

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
            messagebox.showerror("Error", "No plugin selected.")
            return

        plugin_name = plugins_listbox.get(selected_idx).split(" (")[0]
        plugins = plugin_manager.discover_plugins()
        selected_plugin = next((p for p in plugins if p["name"] == plugin_name), None)

        if selected_plugin:
            module = plugin_manager.load_plugin(selected_plugin["path"], selected_plugin["main"])
            if hasattr(module, "main"):
                module.main(frame)
            else:
                messagebox.showerror("Error", "Plugin does not have a main function.")

    button_frame = ttk.Frame(root)
    button_frame.pack(fill=tk.X, pady=10)

    ttk.Button(button_frame, text="Load Plugins", command=load_plugins).pack(side=tk.LEFT, padx=5)
    ttk.Button(button_frame, text="Launch Plugin", command=launch_plugin).pack(side=tk.LEFT, padx=5)
    ttk.Button(button_frame, text="Download Plugin", command=lambda: download_plugin_window(plugin_manager)).pack(side=tk.LEFT, padx=5)

    load_plugins()
    root.mainloop()

if __name__ == "__main__":
    create_ui()
