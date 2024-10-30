import tkinter as tk
from PIL import Image, ImageTk, ImageSequence
import random
import pygame

print("you can minimize this window :)")
# Initialize pygame mixer for sound playback
pygame.mixer.init()

# Constants for application behavior
RESIZE_FACTOR = 0.5  # Resize factor for images
MOVE_DISTANCE = 5  # Character movement distance
ANIMATION_INTERVAL = 100  # Animation frame interval (milliseconds)
PAUSE_PROBABILITY = 10  # Chance of character pausing (percentage)
PAUSE_DURATION_RANGE = (2000, 5000)  # Pause duration range (milliseconds)

# Load and initialize the sound
sound = pygame.mixer.Sound("CerberWanWan.mp3")


# Function to resize images by a specified factor
def resize_image(image, factor=RESIZE_FACTOR):
    return image.resize(
        (int(image.width * factor), int(image.height * factor))
    )


class DesktopCharacterApp:
    def __init__(self, root):
        # Set up application window properties
        self.root = root
        self.root.title("Desktop Character")
        self.root.overrideredirect(True)  # Remove title bar and window controls
        self.root.attributes("-topmost", True, "-transparentcolor", self.root.cget("bg"))

        # Load character images for both standing and walking animations
        self.standing_photo_right, self.standing_photo_left = self.load_standing_images("cerbyStand.png")
        self.walking_frames_right, self.walking_frames_left = self.load_walking_images("cerby-walk.webp")

        # Initialize character properties
        self.x_pos, self.y_pos = 200, 200  # Set starting position of the character
        self.direction = "right"  # Set initial direction
        self.is_paused = False  # Set initial paused state
        self.is_on_top = True  # Set 'always on top' setting
        self.current_frame = 0  # Track current animation frame
        self.sound_enabled = True  # Initialize sound setting as enabled
        self.menu = tk.Menu(self.root, tearoff=0)  # Initialize menu here

        # Initialize drag operation values
        self.offset_x = 0
        self.offset_y = 0

        # Create character label and set initial image
        self.label = tk.Label(self.root, bd=0, bg=self.root.cget("bg"))
        self.label.pack()
        self.label.configure(image=self.standing_photo_right)

        # Initialize user interactions and start the animation
        self.bind_events()
        self.animate_walk()  # Start animation

    # Load and flip images for the standing animation
    @staticmethod
    def load_standing_images(path):
        image = resize_image(Image.open(path))
        return (
            ImageTk.PhotoImage(image),
            ImageTk.PhotoImage(image.transpose(Image.Transpose.FLIP_LEFT_RIGHT))
        )

    # Load frames for walking animation
    @staticmethod
    def load_walking_images(path):
        image = Image.open(path)
        return (
            [ImageTk.PhotoImage(resize_image(frame.copy())) for frame in ImageSequence.Iterator(image)],
            [ImageTk.PhotoImage(resize_image(frame.copy().transpose(Image.Transpose.FLIP_LEFT_RIGHT))) for frame in
             ImageSequence.Iterator(image)]
        )

    # Controls frame updates for walking animation
    def animate_walk(self):
        if not self.is_paused:
            frames = self.walking_frames_right if self.direction == "right" else self.walking_frames_left
            self.label.configure(image=frames[self.current_frame])
            self.current_frame = (self.current_frame + 1) % len(frames)
            self.update_position()  # Update position in each frame

        # Determine if character should pause
        should_pause = random.randint(1, 100) <= PAUSE_PROBABILITY
        if should_pause:
            self.is_paused = True
            self.label.configure(
                image=self.standing_photo_right if self.direction == "right" else self.standing_photo_left)
            # Resume movement after a random interval within defined range
            self.root.after(random.randint(*PAUSE_DURATION_RANGE), self.resume_movement)
        else:
            self.root.after(ANIMATION_INTERVAL, self.animate_walk)  # Continue animation loop

    # Update position based on direction and screen boundaries
    def update_position(self):
        self.x_pos += MOVE_DISTANCE if self.direction == "right" else -MOVE_DISTANCE
        if self.x_pos >= self.root.winfo_screenwidth() - self.walking_frames_right[0].width() or self.x_pos <= 0:
            self.direction = "left" if self.direction == "right" else "right"
        self.root.geometry(f"+{self.x_pos}+{self.y_pos}")

    # Resume movement by restarting the animation loop
    def resume_movement(self):
        self.is_paused = False
        self.animate_walk()

    # Toggle the sound setting and update the menu label
    def toggle_sound(self):
        self.sound_enabled = not self.sound_enabled
        self.menu.entryconfig(0, label="Sound On" if not self.sound_enabled else "Sound Off")

    # Play sound if sound is enabled
    def play_sound(self):
        if self.sound_enabled:
            sound.play()

    # Initialize drag offsets at the start of drag
    def start_drag(self, event):
        self.offset_x, self.offset_y = event.x, event.y

    # Update character position based on drag motion
    def do_drag(self, event):
        self.x_pos, self.y_pos = event.x_root - self.offset_x, event.y_root - self.offset_y
        self.root.geometry(f"+{self.x_pos}+{self.y_pos}")

    # Toggle the 'always on top' window setting
    def toggle_on_top(self):
        self.is_on_top = not self.is_on_top
        self.root.attributes("-topmost", self.is_on_top)

    # Close the application
    def exit_app(self):
        self.root.quit()

    # Set up right-click context menu and bind events
    def bind_events(self):
        self.menu.add_command(label="Sound Off", command=self.toggle_sound)
        self.menu.add_command(label="Toggle Always on Top", command=self.toggle_on_top)
        self.menu.add_command(label="Exit", command=self.exit_app)

        # Bind events for dragging, menu, and sound playback
        self.root.bind("<Button-1>", self.start_drag)  # Start drag
        self.root.bind("<B1-Motion>", self.do_drag)  # Drag motion
        self.root.bind("<Button-3>", self.show_menu)  # Right-click menu
        self.label.bind("<Button-1>", lambda e: self.play_sound())  # Play sound on left-click

    # Display the context menu at the cursor position
    def show_menu(self, event):
        self.menu.tk_popup(event.x_root, event.y_root)


# Initialize and run the application
app_root = tk.Tk()
app = DesktopCharacterApp(app_root)
app_root.mainloop()
