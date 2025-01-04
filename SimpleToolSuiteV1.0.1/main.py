import os
import importlib.util
import tkinter as tk
from tkinter import ttk, messagebox, filedialog, simpledialog
import json
import requests


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
                                "path": plugin_path,
                                "main": metadata.get("main", "main.py")
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
            plugins_listbox.insert(tk.END, plugin["name"])

    def launch_plugin():
        selected_idx = plugins_listbox.curselection()
        if not selected_idx:
            messagebox.showerror("Error", "No plugin selected")
            return

        plugin_name = plugins_listbox.get(selected_idx)
        plugins = plugin_manager.discover_plugins()
        selected_plugin = next((p for p in plugins if p["name"] == plugin_name), None)

        if selected_plugin:
            module = plugin_manager.load_plugin(selected_plugin["path"], selected_plugin["main"])
            if hasattr(module, "main"):
                module.main(frame)  # Pass the frame as the parent for the plugin UI
            else:
                messagebox.showerror("Error", "Plugin does not have a main function")



    def download_plugin():
        """Download a plugin from the repository."""
        repo_url = "https://api.github.com/repos/MaxTheSpy/SimpleToolSuite/contents/SimpleToolSuiteV1.0.1/plugins"
        plugin_name = simpledialog.askstring("Download Plugin", "Enter the plugin name:")

        if not plugin_name:
            return

        plugin_url = f"{repo_url}/{plugin_name}"
        response = requests.get(plugin_url)

        if response.status_code == 200:
            try:
                plugin_data = response.json()
                for file in plugin_data:
                    if file["type"] == "file":
                        file_url = file["download_url"]
                        file_path = os.path.join(plugin_manager.plugin_dir, plugin_name, file["name"])
                        os.makedirs(os.path.dirname(file_path), exist_ok=True)
                        with open(file_path, "wb") as f:
                            f.write(requests.get(file_url).content)

                messagebox.showinfo("Success", f"{plugin_name} downloaded and installed.")
                load_plugins()  # Refresh the plugin list
            except Exception as e:
                messagebox.showerror("Error", f"Failed to download plugin: {e}")
        else:
            messagebox.showerror("Error", "Failed to download plugin. Check the plugin name or repository URL.")



    # Buttons
    button_frame = ttk.Frame(root)
    button_frame.pack(fill=tk.X, pady=10)

    load_button = ttk.Button(button_frame, text="Load Plugins", command=load_plugins)
    load_button.pack(side=tk.LEFT, padx=5)

    launch_button = ttk.Button(button_frame, text="Launch Plugin", command=launch_plugin)
    launch_button.pack(side=tk.LEFT, padx=5)

    download_button = ttk.Button(button_frame, text="Download Plugin", command=download_plugin)
    download_button.pack(side=tk.LEFT, padx=5)

    # Auto-load plugins on startup
    load_plugins()

    root.mainloop()



if __name__ == "__main__":
    create_ui()
