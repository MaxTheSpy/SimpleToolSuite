import os
from PyQt5 import QtWidgets, uic


class IllegalCharacterReplacementTool(QtWidgets.QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)

        # Force resolution to the SimpleToolSuite directory
        script_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))
        plugin_dir = os.path.join(script_dir, "plugins", "IllegalCharacterReplacement")
        ui_path = os.path.join(plugin_dir, "icrt_ui.ui")
        uic.loadUi(ui_path, self)

        # Set default values
        self.lineEdit_ill_char.setText('<>:"/\\|?*')
        self.lineEdit_rep_char.setText('-')

        # Connect UI elements to logic
        self.pushButton_select_2.clicked.connect(self.select_directory)
        self.pushButton_analyze_2.clicked.connect(self.analyze_directory)

        # Set up the table widget
        self.tableView_results_2.setColumnCount(4)
        self.tableView_results_2.setHorizontalHeaderLabels(["Name", "Target Character", "Override", "Action"])

        # Configure column widths
        header = self.tableView_results_2.horizontalHeader()
        header.setSectionResizeMode(0, QtWidgets.QHeaderView.Stretch)  # "Name" column adjusts freely
        header.setSectionResizeMode(1, QtWidgets.QHeaderView.Stretch)  # "Target Character" column adjusts freely
        header.setSectionResizeMode(2, QtWidgets.QHeaderView.Fixed)    # "Override" column has fixed width
        header.setSectionResizeMode(3, QtWidgets.QHeaderView.Fixed)    # "Action" column has fixed width
        self.tableView_results_2.setColumnWidth(2, 100)  # Lock the "Override" column to 100px
        self.tableView_results_2.setColumnWidth(3, 100)  # Lock the "Action" column to 100px

        # Initialize file list
        self.files_with_issues = []

    def select_directory(self):
        """Open a dialog to select a directory."""
        directory = QtWidgets.QFileDialog.getExistingDirectory(self, "Select Directory")
        if directory:
            self.lineEdit_directory_2.setText(directory)

    def analyze_directory(self):
        """Analyze the directory for files and folders with illegal characters."""
        directory = self.lineEdit_directory_2.text().strip()
        illegal_chars = self.lineEdit_ill_char.text().strip()

        if not directory:
            QtWidgets.QMessageBox.warning(self, "Error", "Please select a directory.")
            return

        if not illegal_chars:
            QtWidgets.QMessageBox.warning(self, "Error", "Please specify illegal characters.")
            return

        # Find files and directories with illegal characters
        self.files_with_issues = self.find_files_with_issues(directory, illegal_chars)

        # Populate the table with results
        self.populate_results_table(illegal_chars)

    def find_files_with_issues(self, directory, illegal_chars):
        """Find all files and directories with illegal characters."""
        files_with_issues = []
        for root, dirs, files in os.walk(directory):
            for name in dirs + files:
                if any(char in name for char in illegal_chars):
                    files_with_issues.append((root, name))
        return files_with_issues

    def populate_results_table(self, illegal_chars):
        """Populate the results table with files and folders containing illegal characters."""
        # Clear the table
        self.tableView_results_2.setRowCount(0)

        # Populate rows
        for root, name in self.files_with_issues:
            # Extract just the file/folder name
            file_name = name

            # Find the first illegal character
            target_character = next((char for char in name if char in illegal_chars), "")

            # Add a new row
            row_position = self.tableView_results_2.rowCount()
            self.tableView_results_2.insertRow(row_position)

            # Add file/folder name
            self.tableView_results_2.setItem(row_position, 0, QtWidgets.QTableWidgetItem(file_name))

            # Add target character
            self.tableView_results_2.setItem(row_position, 1, QtWidgets.QTableWidgetItem(target_character))

            # Add an Override field (QLineEdit)
            override_field = QtWidgets.QLineEdit()
            override_field.setMaxLength(1)  # Only allow a single character
            self.tableView_results_2.setCellWidget(row_position, 2, override_field)

            # Add a Replace button
            replace_button = QtWidgets.QPushButton("Replace")
            replace_button.setMaximumWidth(100)  # Keep button width consistent
            replace_button.clicked.connect(lambda _, r=root, n=name, b=replace_button: self.confirm_or_replace(r, n, b, override_field))
            self.tableView_results_2.setCellWidget(row_position, 3, replace_button)

    def confirm_or_replace(self, root, name, button, override_field):
        """Handle the Replace button click."""
        if button.text() == "Replace":
            # First click: Change the button text to "Sure?"
            button.setText("Sure?")
        elif button.text() == "Sure?":
            # Second click: Perform the rename and reset the button
            self.replace_illegal_characters(root, name, override_field)
            button.setText("Done")
            button.setEnabled(False)  # Disable the button after renaming

    def replace_illegal_characters(self, root, name, override_field):
        """Replace illegal characters in a specific file or folder."""
        illegal_chars = self.lineEdit_ill_char.text().strip()
        replacement = self.lineEdit_rep_char.text().strip()
        override = override_field.text().strip()

        if not illegal_chars or len(replacement) > 1:
            QtWidgets.QMessageBox.warning(self, "Error", "Invalid replacement settings.")
            return

        # Use override if specified, otherwise use the default replacement
        replacement_char = override if override else replacement

        old_path = os.path.join(root, name)
        new_name = self.sanitize_data(name, illegal_chars, replacement_char)
        new_path = os.path.join(root, new_name)

        try:
            os.rename(old_path, new_path)
            # Refresh the list silently without pop-ups
            self.analyze_directory()  # Refresh the list
        except Exception as e:
            QtWidgets.QMessageBox.critical(self, "Error", f"Failed to rename:\n\n{old_path}\n\nError: {e}")

    def sanitize_data(self, value, illegal_chars, replacement):
        """Sanitize a string by replacing illegal characters."""
        for char in illegal_chars:
            value = value.replace(char, replacement)
        return value


def main(parent=None):
    """Main entry point for the plugin."""
    widget = IllegalCharacterReplacementTool(parent)
    if parent is None:
        widget.show()
    return widget


if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    window = IllegalCharacterReplacementTool()
    window.show()
    sys.exit(app.exec_())
