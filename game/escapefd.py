import tkinter as tk
import random
from collections import deque
import pickle
import os
import math

BASE_GRID_SIZE = 6
CELL_SIZE = 60
ANIMATION_STEPS = 12
ANIMATION_DELAY = 10  # ms

SPIKE_COUNT = 3
TURRET_COUNT = 2

SAVE_FILE = "savepe.beta"

ACHIEVEMENTS = [
    (3, "Escaped 3 times!"),
    (5, "Evaded the duck 5 times!"),
    (10, "Duck Master: 10 Escapes!"),
]

# Modern color palette
BG_DARK = "#181c24"
BG_PANEL = "#232a34"
FG_LIGHT = "#e0e0e0"
ACCENT = "#43e97b"
ACCENT2 = "#4caf50"
DANGER = "#f44336"
TURRET = "#888"
SPIKE = "#bdb76b"
LASER = "#ffe066"
PLAYER = "#2196f3"
EXIT = "#43e97b"
BORDER = "#2c3440"
GOLD = "#ffd700"

class Game:
    def __init__(self, root):
        self.root = root
        self.root.option_add("*Font", "Arial 13")
        self.root.option_add("*Button.relief", "flat")
        self.root.option_add("*Button.bd", 0)
        self.root.option_add("*Button.highlightThickness", 0)
        self.root.option_add("*Button.activeBackground", ACCENT)
        self.root.option_add("*Button.activeForeground", BG_DARK)
        self.root.option_add("*Label.bg", BG_DARK)
        self.root.option_add("*Label.fg", FG_LIGHT)
        self.load_data()
        self.notification = None
        self.main_menu_animating = False
        self.main_menu()

    def load_data(self):
        if os.path.exists(SAVE_FILE):
            try:
                with open(SAVE_FILE, "rb") as f:
                    data = pickle.load(f)
                self.level = data.get("level", 1)
                self.escapes = data.get("escapes", 0)
                self.achievements_unlocked = set(data.get("achievements", []))
            except Exception:
                self.level = 1
                self.escapes = 0
                self.achievements_unlocked = set()
        else:
            self.level = 1
            self.escapes = 0
            self.achievements_unlocked = set()

    def save_data(self):
        data = {
            "level": self.level,
            "escapes": self.escapes,
            "achievements": list(self.achievements_unlocked)
        }
        with open(SAVE_FILE, "wb") as f:
            pickle.dump(data, f)

    def delete_data(self):
        if os.path.exists(SAVE_FILE):
            os.remove(SAVE_FILE)
        self.level = 1
        self.escapes = 0
        self.achievements_unlocked = set()
        self.main_menu()

    def main_menu(self):
        self.clear_root()
        self.main_menu_animating = True
        self.menu_frame = tk.Frame(self.root, bg=BG_DARK)
        self.menu_frame.pack(fill="both", expand=True)
        tk.Label(
            self.menu_frame, text="Escape from Duck",
            font=("Arial Black", 38), fg=ACCENT, bg=BG_DARK
        ).pack(pady=(60, 30))
        # Animated canvas
        self.menu_canvas = tk.Canvas(self.menu_frame, width=480, height=180, bg=BG_DARK, highlightthickness=0, bd=0)
        self.menu_canvas.pack(pady=(0, 18))
        self.menu_ducks = [
            {"x": 60, "y": 90, "dx": 2, "dy": 1, "color": DANGER},
            {"x": 420, "y": 60, "dx": -2, "dy": 1, "color": DANGER},
        ]
        self.menu_players = [
            {"x": 120, "y": 120, "dx": 1, "dy": -2, "color": PLAYER},
            {"x": 360, "y": 40, "dx": -1, "dy": 2, "color": PLAYER},
        ]
        self.animate_main_menu()
        btn_style = {
            "font": ("Arial", 20, "bold"),
            "width": 16,
            "bd": 0,
            "highlightthickness": 0,
            "relief": "flat",
            "cursor": "hand2",
            "activebackground": ACCENT,
            "activeforeground": BG_DARK,
            "borderwidth": 0,
            "padx": 6,
            "pady": 6,
        }
        tk.Button(
            self.menu_frame, text="▶ Start Game", bg=ACCENT2, fg=BG_DARK,
            command=self.start_game, **btn_style
        ).pack(pady=18)
        tk.Button(
            self.menu_frame, text="🗑 Delete Data", bg="#333", fg=GOLD,
            command=self.delete_data, **btn_style
        ).pack(pady=6)
        tk.Button(
            self.menu_frame, text="✖ Quit", bg=DANGER, fg=BG_DARK,
            command=self.root.destroy, **btn_style
        ).pack(pady=6)
        # --- Credits button ---
        tk.Button(
            self.menu_frame, text="Credits", bg=BG_PANEL, fg=FG_LIGHT,
            command=self.show_credits, font=("Arial", 14, "italic"),
            relief="flat", cursor="hand2", activebackground=ACCENT, activeforeground=BG_DARK
        ).pack(pady=(18, 0))
        if self.escapes > 0:
            tk.Label(
                self.menu_frame,
                text=f"Escapes: {self.escapes}   Level: {self.level}",
                font=("Arial", 16, "bold"), fg=FG_LIGHT, bg=BG_DARK
            ).pack(pady=18)
        if self.achievements_unlocked:
            tk.Label(
                self.menu_frame, text="Achievements:",
                font=("Arial", 15, "bold"), fg=GOLD, bg=BG_DARK
            ).pack()
            for ach in self.achievements_unlocked:
                tk.Label(
                    self.menu_frame, text=ach,
                    font=("Arial", 13), fg=GOLD, bg=BG_DARK
                ).pack()

    def show_credits(self):
        credits_win = tk.Toplevel(self.root)
        credits_win.title("Credits")
        credits_win.configure(bg=BG_DARK)
        credits_win.resizable(False, False)
        tk.Label(
            credits_win,
            text="Escape from Duck\n\nCreated by AbramichS\n(Sargis Grigoryan)\n2015-2025",
            font=("Arial", 16, "bold"), fg=ACCENT, bg=BG_DARK, pady=18
        ).pack(padx=30, pady=20)
        tk.Button(
            credits_win, text="Close", command=credits_win.destroy,
            font=("Arial", 14), bg=ACCENT2, fg=BG_DARK, relief="flat", padx=12, pady=6
        ).pack(pady=(0, 18))

    def animate_main_menu(self):
        if not self.main_menu_animating:
            return
        self.menu_canvas.delete("all")
        # Animate ducks
        for d in self.menu_ducks:
            d["x"] += d["dx"]
            d["y"] += d["dy"]
            if d["x"] < 30 or d["x"] > 450:
                d["dx"] *= -1
            if d["y"] < 30 or d["y"] > 150:
                d["dy"] *= -1
            self.menu_canvas.create_oval(
                d["x"]-24, d["y"]-24, d["x"]+24, d["y"]+24,
                fill=d["color"], outline="#fff", width=3
            )
        # Animate players
        for p in self.menu_players:
            p["x"] += p["dx"]
            p["y"] += p["dy"]
            if p["x"] < 30 or p["x"] > 450:
                p["dx"] *= -1
            if p["y"] < 30 or p["y"] > 150:
                p["dy"] *= -1
            self.menu_canvas.create_rectangle(
                p["x"]-20, p["y"]-20, p["x"]+20, p["y"]+20,
                fill=p["color"], outline="#fff", width=3
            )
        self.root.after(24, self.animate_main_menu)

    def clear_root(self):
        self.main_menu_animating = False
        for widget in self.root.winfo_children():
            widget.destroy()

    def start_game(self):
        self.clear_root()
        self.is_running = True
        self.grid_size = BASE_GRID_SIZE + (self.level - 1) // 3  # Increase grid size every 3 levels
        self.randomize_level()
        self.top_panel = tk.Frame(self.root, bg=BG_PANEL)
        self.top_panel.pack(fill="x")
        self.notification_label = tk.Label(
            self.top_panel, text="", font=("Arial", 16, "bold"),
            fg=GOLD, bg=BG_PANEL, pady=8
        )
        self.notification_label.pack(fill="x")
        self.canvas = tk.Canvas(
            self.root, width=self.grid_size*CELL_SIZE, height=self.grid_size*CELL_SIZE,
            bg=BG_PANEL, highlightthickness=0, bd=0
        )
        self.canvas.pack(pady=(0, 8))
        self.status = tk.Label(
            self.root,
            text=f"Level {self.level}   Escapes: {self.escapes}   Use arrows or WASD",
            font=("Arial", 15, "bold"), bg=BG_DARK, fg=FG_LIGHT, pady=8
        )
        self.status.pack(fill="x")
        # Fast repeat for holding keys
        self.root.bind("<KeyPress>", self.key_down)
        self.root.bind("<KeyRelease>", self.key_up)
        self.held_key = None
        self.key_repeat_id = None
        self.draw()

    def set_status(self, text):
        if hasattr(self, "status") and self.status.winfo_exists():
            self.status.config(text=text)

    def key_down(self, event):
        keymap = {
            "Up": 'w', "Down": 's', "Left": 'a', "Right": 'd',
            "w": 'w', "a": 'a', "s": 's', "d": 'd'
        }
        if event.keysym in keymap and self.held_key is None:
            self.held_key = keymap[event.keysym]
            self.handle_input(self.held_key)
            self.key_repeat_id = self.root.after(120, self.repeat_key)
        elif event.keysym == "q":
            self.quit_game()

    def key_up(self, event):
        keymap = {
            "Up": 'w', "Down": 's', "Left": 'a', "Right": 'd',
            "w": 'w', "a": 'a', "s": 's', "d": 'd'
        }
        if event.keysym in keymap and self.held_key == keymap[event.keysym]:
            self.held_key = None
            if self.key_repeat_id:
                self.root.after_cancel(self.key_repeat_id)
                self.key_repeat_id = None

    def repeat_key(self):
        if self.held_key:
            self.handle_input(self.held_key)
            self.key_repeat_id = self.root.after(60, self.repeat_key)

    def randomize_level(self):
        positions = [(x, y) for x in range(self.grid_size) for y in range(self.grid_size)]
        self.player_position = list(random.choice(positions))
        positions.remove(tuple(self.player_position))
        self.win_condition = list(random.choice(positions))
        positions.remove(tuple(self.win_condition))
        self.duck_position = list(random.choice(positions))
        positions.remove(tuple(self.duck_position))
        # Spikes
        self.spikes = set()
        for _ in range(min(SPIKE_COUNT + self.level // 2, self.grid_size * self.grid_size - 5)):
            if not positions:
                break
            spike = random.choice(positions)
            self.spikes.add(spike)
            positions.remove(spike)
        # Turrets
        self.turrets = []
        for _ in range(min(TURRET_COUNT + self.level // 3, self.grid_size * self.grid_size - 5 - len(self.spikes))):
            if not positions:
                break
            turret = random.choice(positions)
            direction = random.choice(['up', 'down', 'left', 'right'])
            self.turrets.append((turret, direction))
            positions.remove(turret)

    def draw(self):
        self.canvas.delete("all")
        # Draw grid
        for i in range(self.grid_size):
            for j in range(self.grid_size):
                self.canvas.create_rectangle(
                    i*CELL_SIZE, j*CELL_SIZE, (i+1)*CELL_SIZE, (j+1)*CELL_SIZE,
                    outline=BORDER, width=2
                )
        # Draw exit
        x, y = self.win_condition
        self.canvas.create_rectangle(
            x*CELL_SIZE+6, y*CELL_SIZE+6, (x+1)*CELL_SIZE-6, (y+1)*CELL_SIZE-6,
            fill=EXIT, outline=ACCENT, width=4
        )
        # Draw spikes
        for sx, sy in self.spikes:
            self.canvas.create_polygon(
                sx*CELL_SIZE+CELL_SIZE//2, sy*CELL_SIZE+12,
                sx*CELL_SIZE+12, sy*CELL_SIZE+CELL_SIZE-12,
                sx*CELL_SIZE+CELL_SIZE-12, sy*CELL_SIZE+CELL_SIZE-12,
                fill=SPIKE, outline="#888", width=2
            )
        # Draw turrets
        for (tx, ty), direction in self.turrets:
            self.canvas.create_oval(
                tx*CELL_SIZE+16, ty*CELL_SIZE+16, (tx+1)*CELL_SIZE-16, (ty+1)*CELL_SIZE-16,
                fill=TURRET, outline="#555", width=3
            )
            # Draw turret barrel
            if direction == 'up':
                self.canvas.create_line(tx*CELL_SIZE+CELL_SIZE//2, ty*CELL_SIZE+16, tx*CELL_SIZE+CELL_SIZE//2, ty*CELL_SIZE, fill=FG_LIGHT, width=5)
            elif direction == 'down':
                self.canvas.create_line(tx*CELL_SIZE+CELL_SIZE//2, (ty+1)*CELL_SIZE-16, tx*CELL_SIZE+CELL_SIZE//2, (ty+1)*CELL_SIZE, fill=FG_LIGHT, width=5)
            elif direction == 'left':
                self.canvas.create_line(tx*CELL_SIZE+16, ty*CELL_SIZE+CELL_SIZE//2, tx*CELL_SIZE, ty*CELL_SIZE+CELL_SIZE//2, fill=FG_LIGHT, width=5)
            elif direction == 'right':
                self.canvas.create_line((tx+1)*CELL_SIZE-16, ty*CELL_SIZE+CELL_SIZE//2, (tx+1)*CELL_SIZE, ty*CELL_SIZE+CELL_SIZE//2, fill=FG_LIGHT, width=5)
        # Draw duck
        dx, dy = self.duck_position
        self.duck = self.canvas.create_oval(
            dx*CELL_SIZE+10, dy*CELL_SIZE+10, (dx+1)*CELL_SIZE-10, (dy+1)*CELL_SIZE-10,
            fill=DANGER, outline="#fff", width=3
        )
        # Draw player
        px, py = self.player_position
        self.player = self.canvas.create_rectangle(
            px*CELL_SIZE+10, py*CELL_SIZE+10, (px+1)*CELL_SIZE-10, (py+1)*CELL_SIZE-10,
            fill=PLAYER, outline="#fff", width=3
        )
        # Draw turret lasers
        for (tx, ty), direction in self.turrets:
            if direction == 'up':
                for y in range(ty-1, -1, -1):
                    self.canvas.create_line(tx*CELL_SIZE+CELL_SIZE//2, (ty)*CELL_SIZE, tx*CELL_SIZE+CELL_SIZE//2, y*CELL_SIZE, fill=LASER, width=2, dash=(2,2))
            elif direction == 'down':
                for y in range(ty+1, self.grid_size):
                    self.canvas.create_line(tx*CELL_SIZE+CELL_SIZE//2, (ty+1)*CELL_SIZE, tx*CELL_SIZE+CELL_SIZE//2, (y+1)*CELL_SIZE, fill=LASER, width=2, dash=(2,2))
            elif direction == 'left':
                for x in range(tx-1, -1, -1):
                    self.canvas.create_line((tx)*CELL_SIZE, ty*CELL_SIZE+CELL_SIZE//2, x*CELL_SIZE, ty*CELL_SIZE+CELL_SIZE//2, fill=LASER, width=2, dash=(2,2))
            elif direction == 'right':
                for x in range(tx+1, self.grid_size):
                    self.canvas.create_line((tx+1)*CELL_SIZE, ty*CELL_SIZE+CELL_SIZE//2, (x+1)*CELL_SIZE, ty*CELL_SIZE+CELL_SIZE//2, fill=LASER, width=2, dash=(2,2))

    def handle_input(self, command):
        if not self.is_running:
            return
        dx, dy = 0, 0
        if command == 'w':
            dy = -1
        elif command == 's':
            dy = 1
        elif command == 'a':
            dx = -1
        elif command == 'd':
            dx = 1
        self.animate_move('player', dx, dy, lambda: self.after_player_move())

    def after_player_move(self):
        # Duck moves only 1 step per player move (smoother, more fair)
        self.smooth_duck_steps = []
        mx, my = self.smart_duck_move()
        if not (mx == 0 and my == 0):
            self.smooth_duck_steps.append((mx, my))
            # Actually move the duck position for next step calculation
            self.duck_position[0] += mx
            self.duck_position[1] += my
        # Reset duck position for animation
        for mx, my in reversed(self.smooth_duck_steps):
            self.duck_position[0] -= mx
            self.duck_position[1] -= my
        self.animate_duck_steps(0)

    def animate_duck_steps(self, idx):
        if idx >= len(self.smooth_duck_steps):
            self.root.after(ANIMATION_STEPS * ANIMATION_DELAY + 1, self.check_status)
            return
        mx, my = self.smooth_duck_steps[idx]
        self.animate_move('duck', mx, my, lambda: self.animate_duck_steps(idx+1))

    def animate_move(self, who, dx, dy, callback):
        if dx == 0 and dy == 0:
            callback()
            return
        if who == 'player':
            pos = self.player_position
            shape = self.player
        else:
            pos = self.duck_position
            shape = self.duck
        nx, ny = pos[0] + dx, pos[1] + dy
        if not (0 <= nx < self.grid_size and 0 <= ny < self.grid_size):
            callback()
            return
        step_x = (nx - pos[0]) * CELL_SIZE / ANIMATION_STEPS
        step_y = (ny - pos[1]) * CELL_SIZE / ANIMATION_STEPS
        def do_step(step=1):
            try:
                self.canvas.move(shape, step_x, step_y)
            except tk.TclError:
                return  # Shape was deleted, abort animation
            if step < ANIMATION_STEPS:
                self.root.after(ANIMATION_DELAY, lambda: do_step(step+1))
            else:
                pos[0], pos[1] = nx, ny
                self.draw()
                callback()
        do_step()

    def smart_duck_move(self):
        # BFS pathfinding: duck always takes shortest path to player, avoiding spikes and turrets
        px, py = self.player_position
        dx, dy = self.duck_position

        grid = [[True for _ in range(self.grid_size)] for _ in range(self.grid_size)]
        for sx, sy in self.spikes:
            grid[sx][sy] = False
        for (tx, ty), _ in self.turrets:
            grid[tx][ty] = False

        visited = [[False for _ in range(self.grid_size)] for _ in range(self.grid_size)]
        queue = deque()
        queue.append((dx, dy, []))
        visited[dx][dy] = True

        while queue:
            x, y, path = queue.popleft()
            if (x, y) == (px, py):
                if path:
                    mx, my = path[0][0] - dx, path[0][1] - dy
                    return mx, my
                else:
                    return 0, 0
            for mx, my in [(-1,0),(1,0),(0,-1),(0,1)]:
                nx, ny = x + mx, y + my
                if 0 <= nx < self.grid_size and 0 <= ny < self.grid_size:
                    if not visited[nx][ny] and grid[nx][ny]:
                        visited[nx][ny] = True
                        queue.append((nx, ny, path + [(nx, ny)]))
        # No path found, stay in place
        return 0, 0

    def random_duck_move(self):
        moves = [(-1,0),(1,0),(0,-1),(0,1),(0,0)]
        random.shuffle(moves)
        for dx, dy in moves:
            nx, ny = self.duck_position[0] + dx, self.duck_position[1] + dy
            if 0 <= nx < self.grid_size and 0 <= ny < self.grid_size:
                if (nx, ny) not in self.spikes and all((nx, ny) != t[0] for t in self.turrets):
                    return dx, dy
        return 0, 0

    def check_status(self):
        px, py = self.player_position
        # Check spikes
        if (px, py) in self.spikes:
            self.set_status("You stepped on spikes! Press any key for menu.")
            self.is_running = False
            self.show_notification("")
            self.save_data()
            self.bind_menu_return()
            return
        # Check and remove turret if player steps on base
        for idx, ((tx, ty), direction) in enumerate(self.turrets):
            if (px, py) == (tx, ty):
                del self.turrets[idx]
                self.set_status("You destroyed a turret!")
                self.draw()
                break
        # Check turrets (laser lines)
        for (tx, ty), direction in self.turrets:
            if direction == 'up' and px == tx and py < ty:
                self.set_status("Hit by turret! Press any key for menu.")
                self.is_running = False
                self.show_notification("")
                self.save_data()
                self.bind_menu_return()
                return
            if direction == 'down' and px == tx and py > ty:
                self.set_status("Hit by turret! Press any key for menu.")
                self.is_running = False
                self.show_notification("")
                self.save_data()
                self.bind_menu_return()
                return
            if direction == 'left' and py == ty and px < tx:
                self.set_status("Hit by turret! Press any key for menu.")
                self.is_running = False
                self.show_notification("")
                self.save_data()
                self.bind_menu_return()
                return
            if direction == 'right' and py == ty and px > tx:
                self.set_status("Hit by turret! Press any key for menu.")
                self.is_running = False
                self.show_notification("")
                self.save_data()
                self.bind_menu_return()
                return
        # Check duck
        if self.player_position == self.duck_position:
            self.set_status("The duck got you! Press any key for menu.")
            self.is_running = False
            self.show_notification("")
            self.save_data()
            self.bind_menu_return()
            return
        # Check win
        if self.player_position == self.win_condition:
            self.escapes += 1
            self.level += 1
            self.set_status("You escaped! Press any key for next level.")
            self.is_running = False
            self.check_achievements()
            self.save_data()
            self.root.unbind("<KeyPress>")
            self.root.unbind("<KeyRelease>")
            self.root.bind("<Key>", lambda e: self.next_level())
            return
        # Normal status
        self.set_status(f"Level {self.level}   Escapes: {self.escapes}   Use arrows or WASD")
        self.show_notification("")

    def bind_menu_return(self):
        self.root.unbind("<KeyPress>")
        self.root.unbind("<KeyRelease>")
        self.root.bind("<Key>", lambda e: self.main_menu())

    def next_level(self):
        self.root.unbind("<Key>")
        self.start_game()

    def check_achievements(self):
        for req, name in ACHIEVEMENTS:
            if self.escapes >= req and name not in self.achievements_unlocked:
                self.achievements_unlocked.add(name)
                if req == 3:
                    self.show_notification(name)
                else:
                    self.show_notification("")
        self.save_data()

    def show_notification(self, text):
        if text:
            self.notification_label.config(text=f"🏆 {text} 🏆")
        else:
            self.notification_label.config(text="")

    def quit_game(self):
        self.save_data()
        self.root.destroy()

if __name__ == "__main__":
    root = tk.Tk()
    root.title("Escape from Duck")
    root.configure(bg=BG_DARK)
    game = Game(root)
    root.mainloop()