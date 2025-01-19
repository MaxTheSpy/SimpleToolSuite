import os
import json
from PyQt5 import QtWidgets, uic
from PyQt5.QtCore import QTimer
from PyQt5.QtGui import QIcon, QPalette, QColor
import pygame

class PomodoroApp(QtWidgets.QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        current_dir = os.path.dirname(os.path.abspath(__file__))
        ui_path = os.path.join(current_dir, "POMO.ui")
        if os.path.exists(ui_path):
            uic.loadUi(ui_path, self)
        else:
            raise FileNotFoundError(f"UI file not found: {ui_path}")

        # Initialize configuration, timer, and sound system
        self.config = {}
        self.load_config()
        self.remaining_time = self.config.get("pomodoro_time", 25 * 60)  # Default to Pomodoro time
        self.running = False
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_timer)

        pygame.mixer.init()
        self.is_playing_sound = False

        self.setup_ui()
        self.update_lcd()  # Update the LCD to show the default Pomodoro time


    def setup_ui(self):
        self.button_pomodoro.clicked.connect(self.set_pomodoro_time)
        self.button_sbreak.clicked.connect(self.set_short_break_time)
        self.button_lbreak.clicked.connect(self.set_long_break_time)
        self.button_lbreak_2.clicked.connect(self.toggle_timer)  # Start/Pause button
        self.button_settings.clicked.connect(self.open_settings)
        self.button_settings.setIcon(QIcon.fromTheme("preferences-system")) # Set gear icon for the settings button
        self.textEdit.setPlainText("Tasks/Notes\n")  # Pre-fill "Tasks/Notes" in the textEdit field

        for button in [self.button_pomodoro, self.button_sbreak, self.button_lbreak, self.button_lbreak_2, self.button_settings]:
            button.clicked.connect(self.stop_sound) # Stop sound on any button click

    def set_pomodoro_time(self):
        self.save_notes()
        self.remaining_time = self.config.get("pomodoro_time", 25 * 60)
        self.update_lcd()
        self.set_lcd_color("#FFFFFF")  # White color for Pomodoro

    def set_short_break_time(self):
        self.save_notes()
        self.remaining_time = self.config.get("short_break_time", 5 * 60)
        self.update_lcd()
        self.set_lcd_color("#D44239")  # Red color for Short Break

    def set_long_break_time(self):
        self.save_notes()
        self.remaining_time = self.config.get("long_break_time", 15 * 60)
        self.update_lcd()
        self.set_lcd_color("#D44239")  # Red color for Long Break

    def toggle_timer(self):
        if self.running:
            self.timer.stop()
            self.button_lbreak_2.setText("Start")
        else:
            self.timer.start(1000)
            self.button_lbreak_2.setText("Pause")
        self.running = not self.running

    def update_timer(self):
        if self.remaining_time > 0:
            self.remaining_time -= 1
            self.update_lcd()
        else:
            self.timer.stop()
            self.button_lbreak_2.setText("Start")
            self.running = False
            self.play_end_sound()

    def update_lcd(self):
        minutes = self.remaining_time // 60
        seconds = self.remaining_time % 60
        self.lcdNumber.display(f"{minutes:02}:{seconds:02}")

    def set_lcd_color(self, color):
        palette = self.lcdNumber.palette()
        palette.setColor(QPalette.WindowText, QColor(color))  # Text color
        palette.setColor(QPalette.Light, QColor(color))       # Border light color
        palette.setColor(QPalette.Dark, QColor(color))        # Border dark color
        self.lcdNumber.setPalette(palette)

    def play_end_sound(self):
        current_dir = os.path.dirname(os.path.abspath(__file__))
        sounds_dir = os.path.join(current_dir, "sounds")

        if self.remaining_time == 0:
            if self.running:
                sound_path = os.path.join(sounds_dir, "break_end.mp3")
            else:
                sound_path = os.path.join(sounds_dir, "pomo_end.mp3")
            if os.path.exists(sound_path):
                if not self.is_playing_sound:
                    self.is_playing_sound = True
                    pygame.mixer.music.load(sound_path)
                    pygame.mixer.music.play(loops=-1)  # Loop indefinitely
            else:
                QtWidgets.QMessageBox.warning(self, "Sound Error", f"Sound file not found: {sound_path}")

    def stop_sound(self):
        if self.is_playing_sound:
            pygame.mixer.music.stop()
            self.is_playing_sound = False

    def save_notes(self):
        self.config["notes"] = self.textEdit.toPlainText()
        self.save_config()

    def load_config(self):
        config_path = os.path.join(os.path.dirname(__file__), "config.json")
        try:
            with open(config_path, "r") as file:
                self.config = json.load(file)
        except FileNotFoundError:
            self.config = {
                "pomodoro_time": 25 * 60,
                "short_break_time": 5 * 60,
                "long_break_time": 15 * 60,
                "notes": "",
            }
            self.save_config()
        self.textEdit.setText(self.config.get("notes", ""))

    def save_config(self):
        config_path = os.path.join(os.path.dirname(__file__), "config.json")
        with open(config_path, "w") as file:
            json.dump(self.config, file, indent=4)

    def open_settings(self):
        dialog = SettingsDialog(self.config, self)
        if dialog.exec_():
            self.config.update(dialog.get_values())
            self.save_config()

class SettingsDialog(QtWidgets.QDialog):
    def __init__(self, config, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Settings")
        self.config = config
        self.initUI()

    def initUI(self):
        layout = QtWidgets.QVBoxLayout()

        layout.addWidget(QtWidgets.QLabel("Pomodoro Time (minutes):"))
        self.line_edit_pomodoro = QtWidgets.QLineEdit(str(self.config.get("pomodoro_time", 25 * 60) // 60))
        layout.addWidget(self.line_edit_pomodoro)

        layout.addWidget(QtWidgets.QLabel("Short Break Time (minutes):"))
        self.line_edit_sbreak = QtWidgets.QLineEdit(str(self.config.get("short_break_time", 5 * 60) // 60))
        layout.addWidget(self.line_edit_sbreak)

        layout.addWidget(QtWidgets.QLabel("Long Break Time (minutes):"))
        self.line_edit_lbreak = QtWidgets.QLineEdit(str(self.config.get("long_break_time", 15 * 60) // 60))
        layout.addWidget(self.line_edit_lbreak)

        self.button_load_default = QtWidgets.QPushButton("Load Default")
        self.button_load_default.clicked.connect(self.load_default)
        layout.addWidget(self.button_load_default)

        self.button_save = QtWidgets.QPushButton("Save")
        self.button_save.clicked.connect(self.accept)
        layout.addWidget(self.button_save)

        self.setLayout(layout)

    def load_default(self):
        self.line_edit_pomodoro.setText("25")
        self.line_edit_sbreak.setText("5")
        self.line_edit_lbreak.setText("15")

    def get_values(self):
        return {
            "pomodoro_time": int(self.line_edit_pomodoro.text()) * 60,
            "short_break_time": int(self.line_edit_sbreak.text()) * 60,
            "long_break_time": int(self.line_edit_lbreak.text()) * 60,
        }

def main(parent_widget=None):
    return PomodoroApp(parent_widget)
