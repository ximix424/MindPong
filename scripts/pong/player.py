import scripts.pong.main as main
from scripts.config import *


# Define paddle properties and functions
class Player:
    def __init__(self, root, canvas, width, height, color):
        self.root = root

        self.canvas = canvas
        self.canvas_width = canvas.winfo_reqwidth()
        self.canvas_height = canvas.winfo_reqheight()
        self.color = color
        self.width = width
        self.height = height
        self.pos = None
        self.speed_factor = 1
        self.id = None
        self.velocity_x_axis = 0
        self.direction = 0
        self.wall_hit = False
        self.start_pos = True
        self.direction_update = False

        self.canvas.bind_all('<KeyPress-Left>', self.move_left)
        self.canvas.bind_all('<KeyPress-Right>', self.move_right)

        self.init()

    def update(self, delta_time):
        self.velocity_x_axis = self.calculate_velocity() * delta_time
        # every time the direction is not updated the player gets slower
        if self.direction_update:
            self.direction_update = False
            self.speed_factor = 1
        else:
            self.speed_factor -= (delta_time * 4)/TIME_TO_STOP_PLAYER
            if self.speed_factor <= 0:
                self.speed_factor = 0



    def calculate_velocity(self):
        if self.start_pos:
            return 0

        if self.direction == 1:
            if self.pos[2] >= self.canvas_width:
                if not self.wall_hit:
                    self.wall_hit = True
                return 0
            if self.pos[0] <= 0:
                if not self.wall_hit:
                    self.wall_hit = True
                    return 0
                else:
                    return 1
            else:
                return 1

        elif self.direction == -1:
            if self.pos[0] <= 0:
                if not self.wall_hit:
                    self.wall_hit = True
                return 0
            elif self.pos[2] >= self.canvas_width:
                if not self.wall_hit:
                    self.wall_hit = True
                    return 0
                else:
                    return -1
            else:
                return -1

    def draw(self):

        self.canvas.move(self.id, self.velocity_x_axis * self.speed_factor, 0)
        self.pos = self.canvas.coords(self.id)

    def reset(self):
        self.canvas.delete(self.id)
        self.start_pos = True
        self.speed_factor = 1
        self.init()

    def init(self):
        """Initializes the paddle object and its position."""
        self.id = self.canvas.create_rectangle(0, 0, self.width, self.height, fill=self.color)
        # Move to initial position
        self.canvas.move(self.id, (self.canvas_width - self.width) / 2, self.canvas_height * 0.9)
        # Update position
        self.pos = self.canvas.coords(self.id)

    def move_left(self, evt):
        # Prevent paddle movement while the game state is not playing
        if self.root.state.name is not main.Playing.name:
            return

        if self.start_pos:
            self.start_pos = False
        self.direction = -1
        self.direction_update = True

    def move_right(self, evt):
        # Prevent paddle movement while the game state is not playing
        if self.root.state.name is not main.Playing.name:
            return

        if self.start_pos is True:
            self.start_pos = False
        self.direction = 1
        self.direction_update = True

