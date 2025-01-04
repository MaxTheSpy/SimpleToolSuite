import os
import tkinter as tk
from tkinter import ttk, filedialog


def sanitize_data(value, illegal_chars, replacement):
    """Sanitize a string by replacing illegal characters."""
    if value is None:
        return ''

    for char in illegal_chars:
        value = value.replace(char, replacement)

    while value.endswith('.') or value.endswith(' '):
        value = value[:-1]

    return value


def count_illegal_characters(directory, illegal_chars):
    """Count the total occurrences of illegal characters in file and folder names."""
    count = 0
    for root, dirs, files in os.walk(directory):
        for name in dirs + files:
            count += sum(1 for char in name if char in illegal_chars)
    return count


def replace_illegal_characters_interactive(directory, illegal_chars, replacement, output_widget, interactive_frame):
    """Replace illegal characters interactively with buttons for 'Replace', 'Skip', and 'All'."""
    items_to_process = []

    # Collect all items with illegal characters
    for root, dirs, files in os.walk(directory):
        for name in dirs + files:
            if any(char in name for char in illegal_chars):
                items_to_process.append((root, name))

    current_index = 0

    def refresh_count():
        """Refresh the total illegal character count and update the output."""
        remaining_count = len(items_to_process) - current_index
        output_widget.insert(tk.END, f"\nRemaining illegal characters to replace: {remaining_count}\n")
        output_widget.yview(tk.END)

    def process_all():
        """Replace all remaining items without prompting."""
        nonlocal current_index

        while current_index < len(items_to_process):
            root, name = items_to_process[current_index]

            # Keep the root path unchanged; only sanitize the name
            old_path = os.path.join(root, name)
            new_name = sanitize_data(name, illegal_chars, replacement)
            new_path = os.path.join(root, new_name)

            try:
                # Rename the file or folder
                os.rename(old_path, new_path)
                output_widget.insert(tk.END, f"[OLD]: {old_path}\n[NEW]: {new_path}\nReplaced.\n")
                output_widget.yview(tk.END)

                # Update items_to_process for nested directories
                if os.path.isdir(new_path):
                    # Update remaining items with the new path
                    for i in range(current_index + 1, len(items_to_process)):
                        sub_root, sub_name = items_to_process[i]
                        if sub_root.startswith(old_path):
                            # Update the root path to the renamed directory
                            new_sub_root = sub_root.replace(old_path, new_path, 1)
                            items_to_process[i] = (new_sub_root, sub_name)
            except FileNotFoundError as e:
                output_widget.insert(tk.END, f"[ERROR]: {e}\nSkipped.\n")
                output_widget.yview(tk.END)

            current_index += 1

        refresh_count()

        # Clear the interactive frame and display completion message
        for widget in interactive_frame.winfo_children():
            widget.destroy()
        output_widget.insert(tk.END, "\nAll replacements completed.\n")
        output_widget.yview(tk.END)


    def next_item():
        """Process the next item in the list."""
        nonlocal current_index
        if current_index < len(items_to_process):
            root, name = items_to_process[current_index]
            old_path = os.path.join(root, name)
            new_name = sanitize_data(name, illegal_chars, replacement)
            new_path = os.path.join(root, new_name)

            output_widget.insert(tk.END, f"\n[OLD]: {old_path}\n")
            output_widget.insert(tk.END, f"[NEW]: {new_path}\n")
            output_widget.yview(tk.END)

            # Create interactive buttons
            def replace_action():
                os.rename(old_path, new_path)
                output_widget.insert(tk.END, "Replaced.\n")
                output_widget.yview(tk.END)
                current_index += 1
                refresh_count()
                next_item()

            def skip_action():
                output_widget.insert(tk.END, "Skipped.\n")
                output_widget.yview(tk.END)
                current_index += 1
                refresh_count()
                next_item()

            # Clear and add buttons
            for widget in interactive_frame.winfo_children():
                widget.destroy()

            replace_button = ttk.Button(interactive_frame, text="Replace", command=replace_action)
            replace_button.pack(side=tk.LEFT, padx=5)
            skip_button = ttk.Button(interactive_frame, text="Skip", command=skip_action)
            skip_button.pack(side=tk.LEFT, padx=5)
            all_button = ttk.Button(interactive_frame, text="All", command=process_all)
            all_button.pack(side=tk.LEFT, padx=5)
        else:
            # No more items to process
            for widget in interactive_frame.winfo_children():
                widget.destroy()
            output_widget.insert(tk.END, "\nInteractive mode completed.\n")
            output_widget.yview(tk.END)

    # Start processing the first item
    refresh_count()
    next_item()


def main(parent):
    """Main entry point for the plugin."""
    frame = ttk.Frame(parent)
    frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

    illegal_chars_var = tk.StringVar(value='<>:"/\\|?*')  # Default illegal characters
    replacement_var = tk.StringVar(value='-')  # Default replacement character
    directory_var = tk.StringVar()

    ttk.Label(frame, text="Directory:").grid(row=0, column=0, sticky="e", padx=5, pady=5)
    directory_entry = ttk.Entry(frame, textvariable=directory_var, width=50)
    directory_entry.grid(row=0, column=1, padx=5, pady=5, sticky="ew")
    ttk.Button(frame, text="Browse", command=lambda: directory_var.set(filedialog.askdirectory())).grid(row=0, column=2, padx=5, pady=5)

    ttk.Label(frame, text="Illegal Characters:").grid(row=1, column=0, sticky="e", padx=5, pady=5)
    ttk.Entry(frame, textvariable=illegal_chars_var).grid(row=1, column=1, padx=5, pady=5, sticky="ew")

    ttk.Label(frame, text="Replacement Character:").grid(row=2, column=0, sticky="e", padx=5, pady=5)
    ttk.Entry(frame, textvariable=replacement_var).grid(row=2, column=1, padx=5, pady=5, sticky="ew")

    output_text = tk.Text(frame, wrap=tk.WORD, height=15)
    output_text.grid(row=4, column=0, columnspan=3, padx=5, pady=5, sticky="nsew")

    interactive_frame = ttk.Frame(frame)
    interactive_frame.grid(row=5, column=0, columnspan=3, pady=10)

    def analyze_directory():
        """Analyze the directory and display the total illegal characters."""
        directory = directory_var.get()
        if not directory:
            output_text.insert(tk.END, "Please select a directory.\n")
            return

        illegal_chars = illegal_chars_var.get()
        total_count = count_illegal_characters(directory, illegal_chars)

        output_text.delete("1.0", tk.END)
        output_text.insert(tk.END, f"Total illegal characters to replace: {total_count}\n")

        if total_count > 0:
            ttk.Button(frame, text="Run Interactive", command=lambda: replace_illegal_characters_interactive(
                directory, illegal_chars, replacement_var.get(), output_text, interactive_frame
            )).grid(row=6, column=0, columnspan=3, pady=10)

    ttk.Button(frame, text="Analyze", command=analyze_directory).grid(row=3, column=0, columnspan=3, pady=10)

    frame.columnconfigure(1, weight=1)
    frame.rowconfigure(4, weight=1)
