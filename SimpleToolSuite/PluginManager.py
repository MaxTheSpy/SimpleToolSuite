import requests
import os
import zipfile
import io

class PluginManager:
    # Other methods...

    def download_plugin(self, repo_url, plugin_name):
        """
        Download a plugin from the repository and save it in the plugin directory.
        """
        # Build the plugin's GitHub contents API URL
        plugin_url = f"{repo_url}/{plugin_name}"

        # Make a request to fetch the plugin metadata from the GitHub API
        response = requests.get(plugin_url)
        if response.status_code != 200:
            print(f"Failed to fetch plugin data: {response.status_code}")
            return False

        # Fetching individual files (e.g., ZIP)
        plugin_files = response.json()
        if not isinstance(plugin_files, list):
            print("Unexpected response format from GitHub API.")
            return False

        # Create the plugin directory if it doesn't exist
        plugin_dir = os.path.join(self.plugin_dir, plugin_name)
        os.makedirs(plugin_dir, exist_ok=True)

        # Download each file in the plugin
        for file in plugin_files:
            if file['type'] == 'file':
                file_response = requests.get(file['download_url'])
                if file_response.status_code == 200:
                    with open(os.path.join(plugin_dir, file['name']), 'wb') as f:
                        f.write(file_response.content)
                else:
                    print(f"Failed to download file: {file['name']}")

        print(f"Plugin {plugin_name} downloaded successfully.")
        return True
