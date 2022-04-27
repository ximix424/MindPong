import tkinter as tk
import tkinter.ttk as ttk
from tkinter import END
from tkinter.scrolledtext import ScrolledText
from abc import abstractmethod

from matplotlib import pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

from scripts.pong.game import Game


class View(tk.Frame):
    @abstractmethod
    def create_view(self):
        """Creates the view"""
        raise NotImplementedError


class ConfigView(View):
    def __init__(self, master):
        super().__init__(master)
        self.spin_boxes = {}
        self.sliders = {}
        self.entries = {}
        self.labels = {}
        self.buttons = {}
        self.combo_boxes = {}
        self.check_buttons = {}
        self.check_button_vars = {}
        self.comment_box = None
        self.figure = None
        self.canvas = None
        self.grid(row=0, column=0, sticky='nsew')

    def create_view(self):
        # Control Frame
        control_frame = tk.Frame(master=self)
        control_frame.columnconfigure(0, weight=1)
        control_frame.grid(row=0, column=0, sticky='nsew')

        # First Column
        self.__build_subject_section(control_frame, "Subject", row=0, column=0)
        self.__build_algorithm_section(control_frame, "Algorithm", row=1, column=0)
        self.__build_trial_section(control_frame, "Trial", row=2, column=0)
        self.__build_comment_section(control_frame, "Comment", row=3, column=0)
        self.__build_button_section(control_frame, row=4, column=0)

        # Second Column
        self.__build_graph_section(control_frame, "Graph", row=0, column=1)
        self.__build_switch_section(control_frame, row=3, column=1)

        # Third Column
        self.__build_plot(control_frame)

    def hide_button(self, label):
        """Hides the button with the given label

        :param any label: the label to identify the button
        :return: None
        """
        self.buttons[label].grid_forget()

    def show_button(self, label, row=0, column=0):
        """Shows the button with the given label

        :param any label: the label to identify the button
        :param int row: the row for the button (default = 0)
        :param int column: the row for the button (default = 0)
        :return: None
        """
        self.buttons[label].grid(padx=10, pady=5, row=row, column=column, sticky="nsew")

    def reset_view(self):
        """Sets the view """
        self.enable_inputs()
        self.hide_button("Stop Session")
        self.hide_button("Save Session")
        self.hide_button("Discard Session")
        self.show_button("Start Session", row=0, column=0)
        self.__clear_comment_box()

    def enable_inputs(self):
        """Helper function to enable the input fields"""
        self.__set_input_state(state='enabled')

    def disable_inputs(self):
        """Helper function to disable the input fields"""
        self.__set_input_state(state='disabled')

    # First Column Sections
    def __build_subject_section(self, frame, label, row, column):
        """Frame where the subject information is filled in (id, age, sex).

        :param any frame: the parent container to place the children in.
        :param str label: the label which is used in the label frame.
        :param int row: the row number in the parent container.
        :param int column: the column number in the parent container.
        :return: None
        """
        label_frame = ttk.LabelFrame(frame, text=label)
        self.__create_entry(label_frame, "ID", row=0, column=0, text_var=tk.IntVar(value=1))
        self.__create_entry(label_frame, "Age", row=0, column=1, text_var=None)
        self.__create_combobox(label_frame, "Sex", values=[], row=0, column=2)
        label_frame.grid(padx=10, pady=5, row=row, column=column, sticky='nsew')

    def __build_algorithm_section(self, frame, label, row, column):
        """Frame where the algorithm parameters are filled in (threshold, f_min, f_max, window_size, window_offset).

        :param any frame: the parent container to place the children in.
        :param str label: the label which is used in the label frame.
        :param int row: the row number in the parent container.
        :param int column: the column number in the parent container.
        :return: None
        """
        label_frame = ttk.LabelFrame(frame, text=label)
        self.__create_entry(label_frame, "Threshold", row=0, column=0, text_var=tk.DoubleVar())
        self.__create_entry(label_frame, "f_min", row=0, column=1, text_var=tk.DoubleVar())
        self.__create_entry(label_frame, "f_max", row=0, column=2, text_var=tk.DoubleVar())
        self.__create_spinbox(label_frame, "window_size", "Sliding Window Size", row=1, column=0, from_=200, to=2000,
                              interval=200)
        self.__create_spinbox(label_frame, "window_offset", "Sliding Window Offset", row=1, column=1, from_=40, to=400,
                              interval=40)
        label_frame.grid(padx=10, pady=5, row=row, column=column, sticky='nsew')

    def __build_trial_section(self, frame, label, row, column):
        """Frame where the trial parameters are filled in (trial_min_duration).

        :param any frame: the parent container to place the children in.
        :param str label: the label which is used in the label frame.
        :param int row: the row number in the parent container.
        :param int column: the column number in the parent container.
        :return: None
        """
        spinbox_frame = ttk.LabelFrame(frame, text=label)
        self.__create_spinbox(spinbox_frame, "trial_min_duration", "Trial Min-Duration", row=0, column=0, from_=800,
                              to=1500, interval=100)
        spinbox_frame.grid(padx=10, pady=5, row=row, column=column, sticky='nsew')

    def __build_comment_section(self, frame, label, row, column):
        """Frame where the comment box is placed in.

        :param any frame: the parent container to place the children in.
        :param str label: the label which is used in the label frame.
        :param int row: the row number in the parent container.
        :param int column: the column number in the parent container.
        :return: None
        """
        comment_box_frame = ttk.LabelFrame(frame, text=label)
        self.comment_box = ScrolledText(comment_box_frame, wrap=tk.WORD, height=4)
        self.comment_box.grid(row=3, column=0, pady=10, padx=10)
        comment_box_frame.grid(padx=10, pady=5, row=row, column=column, sticky='nsew')

    # Second Column Sections
    def __build_graph_section(self, frame, label, row, column):
        """Frame where the checkboxes to toggle the graphs are placed in (C3, C4, C3a, C4a, Label).

        :param any frame: the parent container to place the children in.
        :param str label: the label which is used in the label frame.
        :param int row: the row number in the parent container.
        :param int column: the column number in the parent container.
        :return: None
        """
        graph_frame = ttk.LabelFrame(frame, text=label)
        self.__create_checkbutton(graph_frame, "C3", row=0, column=0, command=None)
        self.__create_checkbutton(graph_frame, "C4", row=1, column=0, command=None)
        self.__create_checkbutton(graph_frame, "C3a", row=2, column=0, command=None)
        self.__create_checkbutton(graph_frame, "C4a", row=3, column=0, command=None)
        self.__create_checkbutton(graph_frame, "Label", row=4, column=0, command=None)
        graph_frame.grid(padx=10, pady=5, row=row, column=column, rowspan=2, sticky='nsew')

    def __build_switch_section(self, frame, row, column):
        """Frame where the checkboxes to toggle overall settings are placed in (Dark-mode, Trial recording).

        :param any frame: the parent container to place the children in.
        :param int row: the row number in the parent container.
        :param int column: the column number in the parent container.
        :return: None
        """
        switch_frame = ttk.Frame(frame)
        # Switch to toggle the recording of trials
        self.__create_checkbutton(switch_frame, "Trial Recording", row=0, column=0, command=None)
        # Switch for dark/light mode (not persisted in the data model)
        self.__create_checkbutton(switch_frame, "Dark-Mode", row=1, column=0, command=self.__toggle_dark_mode)
        switch_frame.grid(row=row, column=column, rowspan=2, sticky='sew')

    def __build_button_section(self, frame, row, column):
        """Frame where the buttons are placed in (start session, stop session, save session).

        :param any frame: the parent container to place the children in.
        :param int row: the row number in the parent container.
        :param int column: the column number in the parent container.
        :return: None
        """
        button_frame = ttk.Frame(frame)
        self.__create_button(button_frame, "Start Session", row=0, column=0)
        self.__create_button(button_frame, "Stop Session", row=0, column=0)
        self.__create_button(button_frame, "Save Session", row=0, column=0)
        self.__create_button(button_frame, "Discard Session", row=0, column=0)
        button_frame.grid(row=row, column=column, sticky="nsew")

    def __build_plot(self, frame):
        from matplotlib.figure import Figure
        self.figure = Figure(figsize=(10, 6), dpi=100)
        # self.figure = plt.figure(tight_layout=True, figsize=(8, 8))
        self.canvas = FigureCanvasTkAgg(self.figure, frame)
        self.canvas.draw()

    def show_plot(self, row, column):
        self.canvas.get_tk_widget().grid(rowspan=5, row=row, column=column, sticky="nsew")

    # Helper functions
    def __create_entry(self, frame, label, row, column, text_var):
        """Creates an entry field with the given parameters.

        :param any frame: the parent container to place the children in.
        :param str label: the label which is used in the label frame.
        :param int row: the row number in the parent container.
        :param int column: the column number in the parent container.
        :param any text_var: the text variable.
        :return: None
        """
        self.labels[label] = ttk.Label(text=label)
        label_frame = tk.LabelFrame(frame, labelwidget=self.labels[label], bd=0)
        self.entries[label] = ttk.Entry(label_frame, textvariable=text_var)
        self.entries[label].grid(padx=5, pady=5, row=1, column=1, sticky='nsew')
        self.entries[label].pack(padx=5, pady=5, expand=1, fill='x')
        label_frame.grid(padx=10, pady=5, row=row, column=column, sticky='nsew')

    def __create_button(self, frame, label, row, column):
        """Creates a button with the given parameters.

        :param any frame: the parent container to place the children in.
        :param str label: the label which is used for the button.
        :param int row: the row number in the parent container.
        :param int column: the column number in the parent container.
        :return: None
        """
        self.buttons[label] = ttk.Button(frame, text=label)
        self.buttons[label].grid(padx=10, pady=5, row=row, column=column, sticky='nsew')

    def __create_combobox(self, frame, label, values, row, column):
        """Creates a combobox with the given parameters

        :param any frame: the parent container to place the children in.
        :param str label: the label which is used for the label frame.
        :param any values: the list of possible values to be selected.
        :param int row: the row number in the parent container.
        :param int column: the column number in the parent container.
        :return: None
        """
        self.labels[label] = ttk.Label(text=label)
        label_frame = tk.LabelFrame(frame, labelwidget=self.labels[label], bd=0)
        self.combo_boxes[label] = ttk.Combobox(label_frame, state="readonly", values=values)
        self.combo_boxes[label].grid(row=0, column=0, padx=5, pady=5, sticky='ew')
        label_frame.grid(padx=10, pady=5, row=row, column=column, sticky='nsew')

    def __create_checkbutton(self, frame, label, row, column, command):
        """Creates a checkbutton with the given parameters.

        By default, the on value is True and the off value is False.

        :param any frame: the parent container to place the children in.
        :param str label: the label which is used for the checkbutton.
        :param int row: the row number in the parent container.
        :param int column: the column number in the parent container.
        :param any command: the command that is triggered when the checkbutton state changes.
        :return: None
        """
        self.check_button_vars[label] = tk.BooleanVar()
        self.check_buttons[label] = ttk.Checkbutton(frame, text=label, style='Switch.TCheckbutton',
                                                    variable=self.check_button_vars[label],
                                                    onvalue=True, offvalue=False, command=command)
        self.check_buttons[label].grid(padx=10, pady=5, row=row, column=column, sticky='nsew')

    def __create_spinbox(self, frame, label, text, row, column, from_, to, interval):
        """Creates a spinbox with the given parameters.

        :param any frame: the parent container to place the children in.
        :param str label: the label which is used for referencing the label and the spinbox itself.
        :param str text: the text which is used for the label frame.
        :param int row: the row number in the parent container.
        :param int column: the column number in the parent container.
        :param int from_: the value for the interval start.
        :param int to: the value for the interval end.
        :param int interval: the value for the spacing of individual values in the interval.
        :return: None
        """
        self.labels[label] = ttk.Label(text=text)
        label_frame = tk.LabelFrame(frame, labelwidget=self.labels[label], bd=0)
        self.spin_boxes[label] = ttk.Spinbox(label_frame, state="readonly", from_=from_, to=to, increment=interval)
        self.spin_boxes[label].grid(row=0, column=0, padx=5, pady=5, sticky="ew")
        label_frame.grid(padx=10, pady=5, row=row, column=column, sticky='nsew')

    def __toggle_dark_mode(self):
        """Toggles the config view between dark and light mode."""
        if self.check_button_vars["Dark-Mode"].get():
            self.master.call("set_theme", "dark")
        else:
            self.master.call("set_theme", "light")

    def __set_input_state(self, state):
        """Sets all the input fields of ConfigView to a given state

        :param any state: the state to set the input fields ('enabled', 'disabled')
        :return: None
        """
        self.entries["ID"].configure(state=state)
        self.entries["Age"].configure(state=state)
        self.combo_boxes["Sex"].configure(state=state)
        self.entries["Threshold"].configure(state=state)
        self.entries["f_min"].configure(state=state)
        self.entries["f_max"].configure(state=state)
        self.spin_boxes["window_size"].configure(state=state)
        self.spin_boxes["window_offset"].configure(state=state)
        self.spin_boxes["trial_min_duration"].configure(state=state)
        self.check_buttons["Trial Recording"].configure(state=state)

    def __clear_comment_box(self):
        """Clears the comment box field"""
        self.comment_box.delete('1.0', END)


class GameView(View):
    def __init__(self, master):
        super().__init__(master)
        self.grid(row=0, column=0, sticky='nsew')
        self.data = None
        self.frames = {}
        self.mind_pong = None
        self.game = None

    def bind_data(self, data):
        self.data = data

    def create_view(self):
        control_frame = tk.Frame(master=self)
        control_frame.columnconfigure(0, weight=1)
        control_frame.grid(row=1, column=1, sticky='nsew')

        self.game = Game(control_frame, self, self.data)
        self.game.grid(row=0, column=0, sticky='nsew')
        self.game.focus_set()
        self.game.tkraise()
