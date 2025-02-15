import tkinter as tk
from tkinter import messagebox, filedialog, colorchooser
import sqlite3
import random
import time
import pygame

# ========= Database Manager =========
class DatabaseManager:
    def __init__(self, db_file="game.db"):
        self.db_file = db_file
        self.init_db()
    
    def get_connection(self):
        return sqlite3.connect(self.db_file)
    
    def init_db(self):
        conn = self.get_connection()
        c = conn.cursor()
        c.execute('''
            CREATE TABLE IF NOT EXISTS users (
                username TEXT PRIMARY KEY,
                password TEXT
            )
        ''')
        c.execute('''
            CREATE TABLE IF NOT EXISTS records (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT,
                level INTEGER,
                timer REAL,
                speed TEXT,
                score INTEGER,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        conn.commit()
        conn.close()
    
    def check_user(self, username, password):
        conn = self.get_connection()
        c = conn.cursor()
        c.execute("SELECT password FROM users WHERE username=?", (username,))
        row = c.fetchone()
        conn.close()
        return row[0] if row else None
    
    def create_user(self, username, password):
        conn = self.get_connection()
        c = conn.cursor()
        c.execute("INSERT INTO users (username, password) VALUES (?,?)", (username, password))
        conn.commit()
        conn.close()
    
    def update_record(self, username, level, timer, speed, score):
        conn = self.get_connection()
        c = conn.cursor()
        c.execute("INSERT INTO records (username, level, timer, speed, score) VALUES (?,?,?,?,?)",
                  (username, level, timer, speed, score))
        conn.commit()
        conn.close()
    
    def get_user_records(self, username):
        conn = self.get_connection()
        c = conn.cursor()
        c.execute("SELECT level, timer, speed, score, timestamp FROM records WHERE username=? ORDER BY timestamp DESC", (username,))
        records = c.fetchall()
        conn.close()
        return records
    
    def search_records(self, level, timer):
        conn = self.get_connection()
        c = conn.cursor()
        c.execute("SELECT username, level, timer, speed, score FROM records WHERE level=? AND timer=? ORDER BY score DESC", (level, timer))
        records = c.fetchall()
        conn.close()
        return records
    
    def get_ranking(self):
        conn = self.get_connection()
        c = conn.cursor()
        c.execute("SELECT username, level, timer, speed, score FROM records ORDER BY score DESC")
        ranking = c.fetchall()
        conn.close()
        return ranking

# ========= Game Logic =========
class Game:
    def __init__(self, username, window_width, window_height, target_width, target_height,
                 target_color, level, disappearance, skin_path, timer_minutes):
        self.username = username
        self.window_width = window_width
        self.window_height = window_height
        self.target_width = target_width
        self.target_height = target_height
        self.target_color = target_color
        self.level = level
        self.disappearance = disappearance
        self.skin_path = skin_path
        self.timer_minutes = timer_minutes
        self.score = 0
        self.game_duration = timer_minutes * 60
        self.start_time = None
        self.targets = []
        self.skin_image = None

    def load_skin(self):
        if self.skin_path:
            try:
                self.skin_image = pygame.image.load(self.skin_path)
                self.skin_image = pygame.transform.scale(self.skin_image, (self.target_width, self.target_height))
            except Exception as e:
                print("Error loading skin:", e)
                self.skin_image = None

    def create_targets(self):
        targets = []
        for _ in range(self.level):
            x = random.randint(0, self.window_width - self.target_width)
            y = random.randint(0, self.window_height - self.target_height)
            targets.append(pygame.Rect(x, y, self.target_width, self.target_height))
        return targets

    def run(self):
        pygame.init()
        screen = pygame.display.set_mode((self.window_width, self.window_height))
        pygame.display.set_caption("Game")
        clock = pygame.time.Clock()
        self.load_skin()
        try:
            color = pygame.Color(self.target_color)
        except ValueError:
            color = (128, 0, 128)
        self.score = 0
        self.start_time = time.time()
        self.targets = self.create_targets()
        last_target_time = time.time()
        disappearance_seconds = None
        if self.disappearance != "None":
            try:
                disappearance_seconds = int(self.disappearance)
            except:
                disappearance_seconds = None

        running = True
        while running:
            clock.tick(60)
            current_time = time.time()
            elapsed = current_time - self.start_time
            remaining = self.game_duration - elapsed
            if remaining <= 0:
                running = False

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    pos = pygame.mouse.get_pos()
                    hit = False
                    for rect in self.targets:
                        if rect.collidepoint(pos):
                            hit = True
                            self.score += self.level
                            self.targets.remove(rect)
                            break
                    if not hit:
                        self.score -= self.level
                    if not self.targets:
                        self.targets = self.create_targets()
                        last_target_time = time.time()

            if disappearance_seconds is not None:
                if current_time - last_target_time >= disappearance_seconds:
                    if self.targets:
                        self.score -= self.level
                        self.targets = self.create_targets()
                        last_target_time = current_time

            screen.fill((255, 255, 255))
            for rect in self.targets:
                if self.skin_image:
                    screen.blit(self.skin_image, rect)
                else:
                    pygame.draw.rect(screen, color, rect)
            font = pygame.font.SysFont(None, 36)
            score_text = font.render(f"Score: {self.score}", True, (0, 0, 0))
            timer_text = font.render(f"Time: {int(remaining)}", True, (0, 0, 0))
            screen.blit(score_text, (10, 10))
            screen.blit(timer_text, (10, 50))
            pygame.display.flip()

        pygame.quit()
        return self.score

# ========= Tkinter GUI =========
class LoginWindow:
    def __init__(self, master, db_manager):
        self.master = master
        self.db_manager = db_manager
        self.master.title("Login")
        tk.Label(master, text="Username:").grid(row=0, column=0, padx=10, pady=10)
        self.username_entry = tk.Entry(master)
        self.username_entry.grid(row=0, column=1, padx=10, pady=10)
        tk.Label(master, text="Password:").grid(row=1, column=0, padx=10, pady=10)
        self.password_entry = tk.Entry(master, show="*")
        self.password_entry.grid(row=1, column=1, padx=10, pady=10)
        tk.Button(master, text="Login", command=self.login).grid(row=2, column=0, padx=10, pady=10)

    def login(self):
        username = self.username_entry.get().strip()
        password = self.password_entry.get().strip()
        if not username or not password:
            messagebox.showerror("Error", "Enter username and password")
            return
        stored = self.db_manager.check_user(username, password)
        if stored is None:
            self.db_manager.create_user(username, password)
            messagebox.showinfo("New User", "New user created")
        elif stored != password:
            messagebox.showerror("Error", "Incorrect password")
            return
        self.master.withdraw()
        SettingsWindow(tk.Toplevel(self.master), username, self.db_manager)

class RecordsWindow:
    def __init__(self, master, db_manager, username):
        self.master = master
        self.db_manager = db_manager
        self.username = username
        self.master.title("Player Records")
        
        criteria_frame = tk.Frame(master)
        criteria_frame.pack(pady=10)
        
        tk.Label(criteria_frame, text="Select game level:").grid(row=0, column=0, padx=5, pady=5, sticky="w")
        self.level_var = tk.IntVar()
        self.level_var.set(1)
        level_options = list(range(1, 11))
        self.level_menu = tk.OptionMenu(criteria_frame, self.level_var, *level_options)
        self.level_menu.grid(row=0, column=1, padx=5, pady=5)
        
        tk.Label(criteria_frame, text="Select countdown timer (minutes):").grid(row=1, column=0, padx=5, pady=5, sticky="w")
        self.timer_var = tk.StringVar()
        self.timer_var.set("1")
        self.timer_entry = tk.Entry(criteria_frame, width=5, textvariable=self.timer_var)
        self.timer_entry.grid(row=1, column=1, padx=5, pady=5)
        
        tk.Button(criteria_frame, text="Search", command=self.search_records).grid(row=2, column=0, columnspan=2, pady=10)
        
        self.results_text = tk.Text(master, width=60, height=20)
        self.results_text.pack(padx=10, pady=10)
    
    def search_records(self):
        self.results_text.delete(1.0, tk.END)
        level = self.level_var.get()
        try:
            timer_val = float(self.timer_var.get())
        except ValueError:
            messagebox.showerror("Error", "Enter a valid numerical value for the timer")
            return
        records = self.db_manager.search_records(level, timer_val)
        if records:
            self.results_text.insert(tk.END, "Username\tLevel\tTimer\tSpeed\tScore\n")
            self.results_text.insert(tk.END, "-"*60 + "\n")
            for rec in records:
                username, lvl, timer_val, speed, score = rec
                self.results_text.insert(tk.END, f"{username}\t{lvl}\t{timer_val}\t{speed}\t{score}\n")
        else:
            self.results_text.insert(tk.END, "No records for selected criteria.")

class SettingsWindow:
    def __init__(self, master, username, db_manager):
        self.master = master
        self.username = username
        self.db_manager = db_manager
        self.master.title(f"Game Settings - {self.username}")
        self.create_widgets()

    def create_widgets(self):
        main_frame = tk.Frame(self.master)
        main_frame.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)
        
        # Window Settings Frame
        window_frame = tk.LabelFrame(main_frame, text="Window Settings", padx=10, pady=10)
        window_frame.pack(fill=tk.X, padx=5, pady=5)
        tk.Label(window_frame, text="Width:").grid(row=0, column=0, sticky="w")
        self.win_width = tk.Entry(window_frame, width=10)
        self.win_width.insert(0, "600")
        self.win_width.grid(row=0, column=1, padx=5, pady=5)
        tk.Label(window_frame, text="Height:").grid(row=0, column=2, sticky="w")
        self.win_height = tk.Entry(window_frame, width=10)
        self.win_height.insert(0, "500")
        self.win_height.grid(row=0, column=3, padx=5, pady=5)
        
        # Target Settings Frame
        target_frame = tk.LabelFrame(main_frame, text="Target Settings", padx=10, pady=10)
        target_frame.pack(fill=tk.X, padx=5, pady=5)
        tk.Label(target_frame, text="Target Size (W x H):").grid(row=0, column=0, sticky="w")
        self.tar_width = tk.Entry(target_frame, width=10)
        self.tar_width.insert(0, "40")
        self.tar_width.grid(row=0, column=1, padx=5, pady=5)
        self.tar_height = tk.Entry(target_frame, width=10)
        self.tar_height.insert(0, "40")
        self.tar_height.grid(row=0, column=2, padx=5, pady=5)
        tk.Label(target_frame, text="Color:").grid(row=1, column=0, sticky="w")
        self.tar_color = tk.Entry(target_frame)
        self.tar_color.insert(0, "purple")
        self.tar_color.grid(row=1, column=1, padx=5, pady=5)
        tk.Button(target_frame, text="Choose Color", command=self.choose_color).grid(row=1, column=2, padx=5, pady=5)
        
        # Game Settings Frame
        game_frame = tk.LabelFrame(main_frame, text="Game Settings", padx=10, pady=10)
        game_frame.pack(fill=tk.X, padx=5, pady=5)
        tk.Label(game_frame, text="Game Level (1-10):").grid(row=0, column=0, sticky="w")
        self.level_var = tk.IntVar(value=1)
        self.level_menu = tk.OptionMenu(game_frame, self.level_var, *list(range(1, 11)))
        self.level_menu.grid(row=0, column=1, padx=5, pady=5)
        tk.Label(game_frame, text="Disappear (sec) or None:").grid(row=1, column=0, sticky="w")
        self.disappear = tk.StringVar(value="None")
        self.disappear_menu = tk.OptionMenu(game_frame, self.disappear, "None", "5", "10", "15", "20")
        self.disappear_menu.grid(row=1, column=1, padx=5, pady=5)
        tk.Label(game_frame, text="Timer (minutes):").grid(row=2, column=0, sticky="w")
        self.timer_entry = tk.Entry(game_frame, width=10)
        self.timer_entry.insert(0, "1")
        self.timer_entry.grid(row=2, column=1, padx=5, pady=5)
        
        # Skin Settings Frame
        skin_frame = tk.LabelFrame(main_frame, text="Skin Settings", padx=10, pady=10)
        skin_frame.pack(fill=tk.X, padx=5, pady=5)
        tk.Label(skin_frame, text="Skin (path):").grid(row=0, column=0, sticky="w")
        self.skin_entry = tk.Entry(skin_frame, width=30)
        self.skin_entry.grid(row=0, column=1, padx=5, pady=5)
        tk.Button(skin_frame, text="Browse", command=self.choose_file).grid(row=0, column=2, padx=5, pady=5)
        
        # Action Buttons Frame
        btn_frame = tk.Frame(main_frame)
        btn_frame.pack(padx=5, pady=10)
        tk.Button(btn_frame, text="View Records", command=self.view_records).pack(side=tk.LEFT, padx=5)
        tk.Button(btn_frame, text="Play", command=self.start_game).pack(side=tk.LEFT, padx=5)
        tk.Button(btn_frame, text="Logout", command=self.logout).pack(side=tk.LEFT, padx=5)

    def choose_color(self):
        color = colorchooser.askcolor()[1]
        if color:
            self.tar_color.delete(0, tk.END)
            self.tar_color.insert(0, color)

    def choose_file(self):
        filename = filedialog.askopenfilename(title="Choose skin",
                                              filetypes=(("Image files", "*.png;*.jpg;*.gif"), ("All files", "*.*")))
        if filename:
            self.skin_entry.delete(0, tk.END)
            self.skin_entry.insert(0, filename)

    def view_records(self):
        RecordsWindow(tk.Toplevel(self.master), self.db_manager, self.username)

    def start_game(self):
        try:
            w = int(self.win_width.get())
            h = int(self.win_height.get())
            tw = int(self.tar_width.get())
            th = int(self.tar_height.get())
            timer = float(self.timer_entry.get())
            if tw > w or th > h:
                messagebox.showerror("Error", "Target size exceeds window size!")
                return
        except ValueError:
            messagebox.showerror("Error", "Please enter valid numbers!")
            return
        
        game = Game(self.username, w, h, tw, th,
                    self.tar_color.get(), self.level_var.get(),
                    self.disappear.get(), self.skin_entry.get().strip(), timer)
        
        self.master.withdraw()  # hide the settings window
        try:
            final_score = game.run()
        finally:
            # Regardless of how the game ends, show the settings window again
            self.master.deiconify()
        
        self.db_manager.update_record(self.username, self.level_var.get(), timer, self.disappear.get(), final_score)
        messagebox.showinfo("Game Over", f"Your score: {final_score}")

    def logout(self):
        self.master.destroy()
        root.deiconify()

if __name__ == "__main__":
    db_manager = DatabaseManager()
    root = tk.Tk()
    LoginWindow(root, db_manager)
    root.mainloop()
