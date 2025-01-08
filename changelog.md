# Changelog

### V1.0.4
* Configuration!
    * Config files are now automatically created and saved on your machine when you first run the software.
    * Config.json can be found:
        * Windows: AppData/Local/SimpleToolSuite/Config.json
        * MacOs: Library/Application Support/SimpleToolSuite/Config.json
        * Linux/Unix: .config/SimpleToolSuite/Config.json.
* New Tab: Settings:
    * You can now select the directory you wish to install your plugins.
    * Button added to open the location of your config.json in your file explorer
    * Dark mode enabled for main app and all plugins.
* Plugin Page:
    * There is now a clear definement between "Your Plugins" and "Download Plugin"
    * Both "Your Plugins" and "Download Plugins" show Name, Version, Author, and Description in the description panel on the right.
    * Downloading plugins will get the files from the SimpleToolSuite Repo and install them to the path you have set in the settings tab, or in the folder you are running the application from if you have not specified a specific directory.
* Visual Changes!
    * Im very new to CSS but I have added 1 dark mode and 1 light mode css. Plugins by default use the same CSS rules as the main application
    * I have redesigned the UI in a few places and moved from sts1 ui to sts2 ui.
    * Fixed settings page where buttons could get cut off.
* Codebase:
    * Restructured pluginmanager.py and SimpleToolSuite.py to handle the new features.
