import platform
import tkinter as tk
from pathlib import Path
from threading import Thread

import scripts.config as config
import scripts.data.acquisition.read_data as read_data
from scripts.mvc.controllers import ConfigController, GameController
from scripts.mvc.models import ConfigData
from scripts.mvc.view import ConfigView, GameView


class App(tk.Tk):
    def __init__(self, *args, **kwargs):
        tk.Tk.__init__(self, *args, **kwargs)

        # Window settings
        self.title("Settings")
        self.resizable(False, False)

        # Set the theme initially to light mode
        theme_data_folder = Path("mvc")
        self.call("source", theme_data_folder / "azure.tcl")
        self.call("set_theme", "light")

        # Initialize data model
        self.__data_model = ConfigData()

        # Initialize the windows
        self.game_window = None
        self.config_window = ConfigWindow(self)
        self.thread = None

        self.__update_controllers()
        self.update()

    def __update_controllers(self):
        """Calls the update method of the controllers"""
        self.config_window.config_controller.update()
        self.after(5, self.__update_controllers)

    def create_game_window(self):
        """Creates the second window (game window) and starts the associated read data thread"""
        self.game_window = GameWindow(self)
        # Starting the thread to read data
        self.thread = Thread(target=read_data.init, args=[self.data_model], daemon=True)
        self.thread.start()
        self.__data_model.session_recording = True

    def destroy_game_window(self):
        """Destroys the second window (game window) and stops the associated read data thread"""
        self.game_window.destroy()
        self.game_window = None
        self.__data_model.session_recording = False
        self.thread.join()

    @property
    def data_model(self):
        return self.__data_model


class ConfigWindow(tk.Frame):
    def __init__(self, master):
        super().__init__(master)
        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=1)
        self.grid(row=0, column=0, sticky='nsew')

        self.config_controller = ConfigController(self)
        self.config_view = ConfigView(master)
        self.config_controller.bind(self.config_view)


class GameWindow(tk.Toplevel):
    def __init__(self, master=None):
        super().__init__(master)
        self.master = master

        # for windows set that the size is correct displayed for different dpi screens
        if platform.system() == 'Windows':
            import ctypes
            try:
                # for Windows 8 and higher
                ctypes.windll.shcore.SetProcessDpiAwareness(2)
            except:
                # for Windows 7 and lower
                ctypes.windll.user32.SetProcessDPIAware()

        # Window settings
        self.minsize(config.WINDOW_WIDTH, config.WINDOW_HEIGHT)
        self.resizable(False, False)

        self.game_controller = GameController(self)  # Create Controller
        self.game_view = GameView(self)  # Create View
        self.game_controller.bind(self.game_view)  # Bind View to Controller


if __name__ == "__main__":
    app = App()
    app.bind("<Escape>", quit)
    app.mainloop()
