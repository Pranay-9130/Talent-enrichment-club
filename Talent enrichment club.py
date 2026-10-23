"""
TALENT ENRICHMENT CLUB - DESKTOP APPLICATION
Modern, responsive GUI with screen auto-adjustment, authentication, and event management.
"""

import os
import sys
import sqlite3
import csv
from pathlib import Path
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from PIL import Image, ImageTk

# Base directory & Assets resolution
SCRIPT_DIR = Path(__file__).resolve().parent
ROOT_DIR = SCRIPT_DIR.parent if (SCRIPT_DIR.parent / 'talent_enrichment_club.db').exists() else SCRIPT_DIR
DB_PATH = ROOT_DIR / 'talent_enrichment_club.db'

# Search assets in both local folder and parent folder
ASSET_PATHS = [
    SCRIPT_DIR / 'assets',
    ROOT_DIR / 'assets',
    ROOT_DIR / 'static' / 'images',
    SCRIPT_DIR
]

def find_asset(filename):
    for p in ASSET_PATHS:
        f = p / filename
        if f.exists():
            return f
    return None

def load_scaled_image(filename, target_w, target_h):
    """Load image safely and scale with high quality Lanczos antialiasing."""
    fpath = find_asset(filename)
    if fpath:
        try:
            im = Image.open(fpath)
            im = im.resize((int(target_w), int(target_h)), Image.Resampling.LANCZOS)
            return ImageTk.PhotoImage(im)
        except Exception as e:
            print(f"Image load error for {filename}: {e}")
    
    # Placeholder if missing
    placeholder = Image.new("RGB", (int(target_w), int(target_h)), color="#172554")
    return ImageTk.PhotoImage(placeholder)

def center_window(window, width, height):
    """Center window on screen while adapting to user screen resolution."""
    window.update_idletasks()
    screen_w = window.winfo_screenwidth()
    screen_h = window.winfo_screenheight()
    w = min(width, int(screen_w * 0.90))
    h = min(height, int(screen_h * 0.88))
    x = max(0, (screen_w - w) // 2)
    y = max(0, (screen_h - h) // 2)
    window.geometry(f"{w}x{h}+{x}+{y}")
    return w, h

# Global Session
current_user = None # {'username', 'name', 'role', ...}
active_registered_member_info = {}

# Initialize SQLite database
def init_db():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS members (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            department TEXT,
            uid TEXT,
            email TEXT,
            event TEXT,
            registered_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE,
            password TEXT,
            name TEXT,
            email TEXT,
            department TEXT,
            uid TEXT,
            role TEXT DEFAULT 'student',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS events (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT,
            category TEXT,
            description TEXT,
            date TEXT,
            venue TEXT,
            max_seats INTEGER DEFAULT 50
        )
    ''')
    cursor.execute('''
        INSERT OR IGNORE INTO users (username, password, name, email, department, uid, role)
        VALUES ('admin', 'admin123', 'Club Administrator', 'admin@talentclub.org', 'Administration', 'ADMIN001', 'admin')
    ''')
    cursor.execute('''
        INSERT OR IGNORE INTO users (username, password, name, email, department, uid, role)
        VALUES ('student', 'student123', 'Alex Morgan', 'alex.m@example.com', 'CSE', 'UID202601', 'student')
    ''')
    conn.commit()
    conn.close()

init_db()

# ==============================================================================
# MAIN LOGIN & AUTHENTICATION SCREEN
# ==============================================================================

class TalentClubApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Talent Enrichment Club - Login")
        self.root.configure(bg="#0f172a")

        # Dynamic sizing for screen adjustment
        self.win_w, self.win_h = center_window(self.root, 1050, 680)

        self.apply_theme()
        self.render_login_view()

    def apply_theme(self):
        style = ttk.Style()
        style.theme_use('clam')
        style.configure("TCombobox", fieldbackground="#1e293b", background="#334155", foreground="#ffffff")
        style.configure("Treeview", 
                        background="#1e293b", 
                        foreground="#f8fafc", 
                        fieldbackground="#1e293b", 
                        rowheight=28)
        style.map("Treeview", background=[('selected', '#2563eb')])
        style.configure("Treeview.Heading", 
                        background="#0f172a", 
                        foreground="#94a3b8", 
                        font=("Segoe UI", 10, "bold"))

    def render_login_view(self):
        # Clear existing widgets
        for widget in self.root.winfo_children():
            widget.destroy()

        main_frame = tk.Frame(self.root, bg="#0f172a")
        main_frame.pack(fill=tk.BOTH, expand=True)

        # Left Column - Visual Club Showcase
        left_frame = tk.Frame(main_frame, bg="#1e293b", width=int(self.win_w * 0.45))
        left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # Load scaled hero / logo
        banner_w = int(self.win_w * 0.42)
        banner_h = int(self.win_h * 0.45)
        self.hero_img = load_scaled_image('hero.png', banner_w, banner_h)

        banner_label = tk.Label(left_frame, image=self.hero_img, bg="#1e293b")
        banner_label.pack(pady=(30, 15), padx=20)

        promo_title = tk.Label(left_frame, 
                               text="TALENT ENRICHMENT CLUB", 
                               font=("Segoe UI", 18, "bold"), 
                               fg="#60a5fa", 
                               bg="#1e293b")
        promo_title.pack(pady=5)

        promo_sub = tk.Label(left_frame, 
                             text="Create • Unite • Excel\nSports • Cultural Arts • Music • Fine Arts", 
                             font=("Segoe UI", 11), 
                             fg="#94a3b8", 
                             bg="#1e293b", 
                             justify=tk.CENTER)
        promo_sub.pack(pady=5)

        # Right Column - Login & Registration Form Card
        right_frame = tk.Frame(main_frame, bg="#0f172a")
        right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=40, pady=40)

        login_card = tk.Frame(right_frame, bg="#1e293b", bd=1, relief="solid", highlightbackground="#334155")
        login_card.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Header with Logo Icon
        header_frame = tk.Frame(login_card, bg="#1e293b")
        header_frame.pack(pady=(25, 20))

        self.logo_small = load_scaled_image('logo.png', 50, 50)
        logo_label = tk.Label(header_frame, image=self.logo_small, bg="#1e293b")
        logo_label.pack(side=tk.LEFT, padx=10)

        title_frame = tk.Frame(header_frame, bg="#1e293b")
        title_frame.pack(side=tk.LEFT)
        tk.Label(title_frame, text="MEMBER PORTAL", font=("Segoe UI", 16, "bold"), fg="#ffffff", bg="#1e293b").pack(anchor="w")
        tk.Label(title_frame, text="Sign in to your club account", font=("Segoe UI", 9), fg="#94a3b8", bg="#1e293b").pack(anchor="w")

        # Form Inputs
        fields_frame = tk.Frame(login_card, bg="#1e293b")
        fields_frame.pack(fill=tk.X, padx=40, pady=10)

        tk.Label(fields_frame, text="Username / Student UID:", font=("Segoe UI", 10, "bold"), fg="#f8fafc", bg="#1e293b").pack(anchor="w", pady=(0, 4))
        self.entry_user = tk.Entry(fields_frame, font=("Segoe UI", 12), bg="#0f172a", fg="#ffffff", insertbackground="#ffffff", bd=1, relief="solid")
        self.entry_user.pack(fill=tk.X, pady=(0, 15), ipady=4)
        self.entry_user.insert(0, "admin")

        tk.Label(fields_frame, text="Password:", font=("Segoe UI", 10, "bold"), fg="#f8fafc", bg="#1e293b").pack(anchor="w", pady=(0, 4))
        self.entry_pass = tk.Entry(fields_frame, font=("Segoe UI", 12), show="*", bg="#0f172a", fg="#ffffff", insertbackground="#ffffff", bd=1, relief="solid")
        self.entry_pass.pack(fill=tk.X, pady=(0, 20), ipady=4)
        self.entry_pass.insert(0, "admin123")

        # Buttons
        btn_login = tk.Button(fields_frame, 
                              text="Sign In", 
                              font=("Segoe UI", 12, "bold"), 
                              bg="#2563eb", 
                              fg="#ffffff", 
                              activebackground="#1d4ed8", 
                              activeforeground="#ffffff", 
                              relief="flat", 
                              cursor="hand2", 
                              command=self.handle_login)
        btn_login.pack(fill=tk.X, pady=(0, 12), ipady=5)

        btn_register = tk.Button(fields_frame, 
                                 text="New Student? Register Here", 
                                 font=("Segoe UI", 10, "bold"), 
                                 bg="#334155", 
                                 fg="#38bdf8", 
                                 activebackground="#475569", 
                                 activeforeground="#ffffff", 
                                 relief="flat", 
                                 cursor="hand2", 
                                 command=self.open_signup_window)
        btn_register.pack(fill=tk.X, ipady=3)

        tip_label = tk.Label(login_card, 
                             text="Test Credentials: [admin / admin123] or [student / student123]", 
                             font=("Segoe UI", 8), 
                             fg="#64748b", 
                             bg="#1e293b")
        tip_label.pack(side=tk.BOTTOM, pady=15)

    def handle_login(self):
        username = self.entry_user.get().strip()
        password = self.entry_pass.get().strip()

        if not username or not password:
            messagebox.showwarning("Input Error", "Please enter both username and password.")
            return

        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users WHERE username = ? AND password = ?", (username, password))
        user = cursor.fetchone()
        conn.close()

        if user:
            global current_user
            current_user = dict(user)
            self.open_dashboard()
        else:
            messagebox.showerror("Login Failed", "Incorrect username or password.")

    def open_signup_window(self):
        signup_win = tk.Toplevel(self.root)
        signup_win.title("Register Student Account - Talent Enrichment Club")
        signup_win.configure(bg="#0f172a")
        center_window(signup_win, 550, 600)

        tk.Label(signup_win, text="STUDENT REGISTRATION", font=("Segoe UI", 16, "bold"), fg="#60a5fa", bg="#0f172a").pack(pady=(20, 15))

        f = tk.Frame(signup_win, bg="#1e293b", bd=1, relief="solid")
        f.pack(fill=tk.BOTH, expand=True, padx=30, pady=(0, 20))

        fields = [
            ("Full Name:", "name"),
            ("Student UID:", "uid"),
            ("Email Address:", "email"),
            ("Department:", "dept"),
            ("Username:", "username"),
            ("Password:", "password"),
        ]

        entries = {}
        for idx, (label, key) in enumerate(fields):
            tk.Label(f, text=label, font=("Segoe UI", 9, "bold"), fg="#ffffff", bg="#1e293b").grid(row=idx*2, column=0, sticky="w", padx=20, pady=(10, 2))
            if key == "dept":
                cb = ttk.Combobox(f, values=["CSE", "AIML", "DS", "ECE", "MECH", "BBA", "BCA", "MCA", "MBA"], state="readonly")
                cb.set("CSE")
                cb.grid(row=idx*2+1, column=0, sticky="ew", padx=20, pady=(0, 5))
                entries[key] = cb
            else:
                ent = tk.Entry(f, font=("Segoe UI", 10), bg="#0f172a", fg="#ffffff", insertbackground="#ffffff", show="*" if key=="password" else "")
                ent.grid(row=idx*2+1, column=0, sticky="ew", padx=20, pady=(0, 5), ipady=3)
                entries[key] = ent

        f.grid_columnconfigure(0, weight=1)

        def save_student():
            vals = {k: entries[k].get().strip() for k in entries}
            if not all(vals.values()):
                messagebox.showwarning("Incomplete", "Please fill in all details.", parent=signup_win)
                return

            try:
                conn = sqlite3.connect(DB_PATH)
                cursor = conn.cursor()
                cursor.execute('''
                    INSERT INTO users (username, password, name, email, department, uid, role)
                    VALUES (?, ?, ?, ?, ?, ?, 'student')
                ''', (vals['username'], vals['password'], vals['name'], vals['email'], vals['dept'], vals['uid']))
                conn.commit()
                conn.close()
                messagebox.showinfo("Success", "Account created successfully! You can now log in.", parent=signup_win)
                signup_win.destroy()
            except sqlite3.IntegrityError:
                messagebox.showerror("Error", "Username already exists. Please choose another.", parent=signup_win)

        btn_save = tk.Button(signup_win, text="Complete Sign Up", font=("Segoe UI", 11, "bold"), bg="#10b981", fg="#ffffff", command=save_student)
        btn_save.pack(pady=10, fill=tk.X, padx=30, ipady=4)

    def open_dashboard(self):
        self.root.withdraw() # Hide login window
        dash_win = tk.Toplevel()
        dash_win.title("Talent Enrichment Club - Dashboard")
        dash_win.configure(bg="#0f172a")

        dw, dh = center_window(dash_win, 1100, 720)

        # Top Bar
        top_bar = tk.Frame(dash_win, bg="#1e293b", height=70)
        top_bar.pack(fill=tk.X)

        dash_win.logo_img = load_scaled_image('logo.png', 48, 48)
        logo_lbl = tk.Label(top_bar, image=dash_win.logo_img, bg="#1e293b")
        logo_lbl.pack(side=tk.LEFT, padx=20, pady=10)

        title_box = tk.Frame(top_bar, bg="#1e293b")
        title_box.pack(side=tk.LEFT, pady=10)
        tk.Label(title_box, text="TALENT ENRICHMENT CLUB", font=("Segoe UI", 16, "bold"), fg="#ffffff", bg="#1e293b").pack(anchor="w")
        tk.Label(title_box, text="Official Central Management Dashboard", font=("Segoe UI", 9), fg="#60a5fa", bg="#1e293b").pack(anchor="w")

        # User Profile & Logout
        user_box = tk.Frame(top_bar, bg="#1e293b")
        user_box.pack(side=tk.RIGHT, padx=20)
        
        user_name = current_user.get('name', 'Member')
        user_role = current_user.get('role', 'student').capitalize()
        tk.Label(user_box, text=f"👤 {user_name} ({user_role})", font=("Segoe UI", 10, "bold"), fg="#38bdf8", bg="#1e293b").pack(side=tk.LEFT, padx=10)

        def logout():
            dash_win.destroy()
            self.root.deiconify()

        tk.Button(user_box, text="Sign Out", font=("Segoe UI", 9, "bold"), bg="#ef4444", fg="#ffffff", relief="flat", cursor="hand2", command=logout).pack(side=tk.LEFT)

        # Main Dashboard Layout (Cards Grid)
        content_frame = tk.Frame(dash_win, bg="#0f172a")
        content_frame.pack(fill=tk.BOTH, expand=True, padx=30, pady=20)

        # Stats Header Strip
        stats_frame = tk.Frame(content_frame, bg="#0f172a")
        stats_frame.pack(fill=tk.X, pady=(0, 20))

        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        total_m = c.execute("SELECT COUNT(*) FROM members").fetchone()[0]
        total_e = c.execute("SELECT COUNT(*) FROM events").fetchone()[0]
        conn.close()

        stat_cards = [
            ("TOTAL REGISTERED MEMBERS", str(total_m), "#2563eb"),
            ("ACTIVE CLUB EVENTS", str(total_e), "#8b5cf6"),
            ("SPORTS & ATHLETICS", "6 Tournaments", "#f59e0b"),
            ("CULTURAL & FINE ARTS", "7 Workshops", "#10b981")
        ]

        for title, val, color in stat_cards:
            cf = tk.Frame(stats_frame, bg="#1e293b", bd=1, relief="solid")
            cf.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=6)
            tk.Label(cf, text=title, font=("Segoe UI", 8, "bold"), fg="#94a3b8", bg="#1e293b").pack(pady=(10, 2))
            tk.Label(cf, text=val, font=("Segoe UI", 14, "bold"), fg=color, bg="#1e293b").pack(pady=(0, 10))

        # Action Buttons Grid with Images
        cards_grid = tk.Frame(content_frame, bg="#0f172a")
        cards_grid.pack(fill=tk.BOTH, expand=True)

        card_w = int(dw * 0.28)
        card_h = int(dh * 0.22)

        dash_win.sports_thumb = load_scaled_image('sports.png', card_w, card_h)
        dash_win.cultural_thumb = load_scaled_image('cultural.png', card_w, card_h)
        dash_win.arts_thumb = load_scaled_image('arts.png', card_w, card_h)

        # Card 1: Register for Event
        c1 = tk.Frame(cards_grid, bg="#1e293b", bd=1, relief="solid")
        c1.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")
        tk.Label(c1, image=dash_win.sports_thumb, bg="#1e293b").pack(padx=10, pady=(10, 5))
        tk.Label(c1, text="Event Registration", font=("Segoe UI", 12, "bold"), fg="#ffffff", bg="#1e293b").pack()
        tk.Label(c1, text="Enroll members into Sports, Cultural & Arts", font=("Segoe UI", 8), fg="#94a3b8", bg="#1e293b").pack(pady=(0, 10))
        tk.Button(c1, text="Open Registration Form", font=("Segoe UI", 10, "bold"), bg="#2563eb", fg="#ffffff", relief="flat", cursor="hand2", command=self.open_registration_window).pack(fill=tk.X, padx=15, pady=(0, 12), ipady=3)

        # Card 2: View Registered Members
        c2 = tk.Frame(cards_grid, bg="#1e293b", bd=1, relief="solid")
        c2.grid(row=0, column=1, padx=10, pady=10, sticky="nsew")
        tk.Label(c2, image=dash_win.cultural_thumb, bg="#1e293b").pack(padx=10, pady=(10, 5))
        tk.Label(c2, text="View Registrations", font=("Segoe UI", 12, "bold"), fg="#ffffff", bg="#1e293b").pack()
        tk.Label(c2, text="Search database & manage enrolled members", font=("Segoe UI", 8), fg="#94a3b8", bg="#1e293b").pack(pady=(0, 10))
        tk.Button(c2, text="View All Members", font=("Segoe UI", 10, "bold"), bg="#8b5cf6", fg="#ffffff", relief="flat", cursor="hand2", command=self.open_view_registration).pack(fill=tk.X, padx=15, pady=(0, 12), ipady=3)

        # Card 3: View Members by Event & Manage Events
        c3 = tk.Frame(cards_grid, bg="#1e293b", bd=1, relief="solid")
        c3.grid(row=0, column=2, padx=10, pady=10, sticky="nsew")
        tk.Label(c3, image=dash_win.arts_thumb, bg="#1e293b").pack(padx=10, pady=(10, 5))
        tk.Label(c3, text="Filter & Manage Events", font=("Segoe UI", 12, "bold"), fg="#ffffff", bg="#1e293b").pack()
        tk.Label(c3, text="Filter by sport/culture and add new events", font=("Segoe UI", 8), fg="#94a3b8", bg="#1e293b").pack(pady=(0, 10))
        
        btn_box = tk.Frame(c3, bg="#1e293b")
        btn_box.pack(fill=tk.X, padx=15, pady=(0, 12))
        tk.Button(btn_box, text="Filter by Event", font=("Segoe UI", 9, "bold"), bg="#10b981", fg="#ffffff", relief="flat", cursor="hand2", command=self.open_event_view_window).pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 4), ipady=3)
        tk.Button(btn_box, text="Manage Events", font=("Segoe UI", 9, "bold"), bg="#f59e0b", fg="#ffffff", relief="flat", cursor="hand2", command=self.open_manage_events).pack(side=tk.RIGHT, fill=tk.X, expand=True, padx=(4, 0), ipady=3)

        cards_grid.grid_columnconfigure(0, weight=1)
        cards_grid.grid_columnconfigure(1, weight=1)
        cards_grid.grid_columnconfigure(2, weight=1)

        dash_win.protocol("WM_DELETE_WINDOW", logout)

    # ==============================================================================
    # STUDENT EVENT REGISTRATION WINDOW
    # ==============================================================================
    def open_registration_window(self):
        reg_win = tk.Toplevel()
        reg_win.title("Student Event Registration - Talent Enrichment Club")
        reg_win.configure(bg="#0f172a")
        center_window(reg_win, 650, 700)

        tk.Label(reg_win, text="STUDENT EVENT REGISTRATION", font=("Segoe UI", 16, "bold"), fg="#60a5fa", bg="#0f172a").pack(pady=(15, 10))

        card = tk.Frame(reg_win, bg="#1e293b", bd=1, relief="solid")
        card.pack(fill=tk.BOTH, expand=True, padx=30, pady=10)

        # Fields
        tk.Label(card, text="Candidate Full Name:", font=("Segoe UI", 10, "bold"), fg="#ffffff", bg="#1e293b").pack(anchor="w", padx=25, pady=(12, 2))
        entry_name = tk.Entry(card, font=("Segoe UI", 11), bg="#0f172a", fg="#ffffff", insertbackground="#ffffff")
        entry_name.pack(fill=tk.X, padx=25, pady=(0, 8), ipady=3)

        tk.Label(card, text="Department:", font=("Segoe UI", 10, "bold"), fg="#ffffff", bg="#1e293b").pack(anchor="w", padx=25, pady=(4, 2))
        combo_dept = ttk.Combobox(card, values=["CSE", "AIML", "DS", "ECE", "MECH", "BBA", "BCA", "MCA", "MBA"], state="readonly")
        combo_dept.set("CSE")
        combo_dept.pack(fill=tk.X, padx=25, pady=(0, 8), ipady=2)

        tk.Label(card, text="Student UID:", font=("Segoe UI", 10, "bold"), fg="#ffffff", bg="#1e293b").pack(anchor="w", padx=25, pady=(4, 2))
        entry_uid = tk.Entry(card, font=("Segoe UI", 11), bg="#0f172a", fg="#ffffff", insertbackground="#ffffff")
        entry_uid.pack(fill=tk.X, padx=25, pady=(0, 8), ipady=3)

        tk.Label(card, text="Email Address:", font=("Segoe UI", 10, "bold"), fg="#ffffff", bg="#1e293b").pack(anchor="w", padx=25, pady=(4, 2))
        entry_email = tk.Entry(card, font=("Segoe UI", 11), bg="#0f172a", fg="#ffffff", insertbackground="#ffffff")
        entry_email.pack(fill=tk.X, padx=25, pady=(0, 8), ipady=3)

        # Auto-fill if student is logged in
        if current_user and current_user.get('role') != 'admin':
            if current_user.get('name'): entry_name.insert(0, current_user['name'])
            if current_user.get('uid'): entry_uid.insert(0, current_user['uid'])
            if current_user.get('email'): entry_email.insert(0, current_user['email'])
            if current_user.get('department'): combo_dept.set(current_user['department'])

        # Event Category Selection
        tk.Label(card, text="Select Event Category & Name:", font=("Segoe UI", 10, "bold"), fg="#38bdf8", bg="#1e293b").pack(anchor="w", padx=25, pady=(10, 4))
        
        cat_frame = tk.Frame(card, bg="#1e293b")
        cat_frame.pack(fill=tk.X, padx=25, pady=(0, 8))

        cat_var = tk.StringVar(value="Sports")

        event_options = {
            "Sports": ["Cricket Championship", "Football League", "Badminton Masters", "Basketball Shootout", "Kabaddi Warriors", "Table Tennis Open"],
            "Cultural": ["Vocal & Instrumental Music", "Choreography & Dance", "Skits & Theatrical Drama", "Standup Comedy Night"],
            "Arts": ["Canvas Oil & Watercolor Painting", "Pencil Sketching & Caricature", "Digital Illustration & Design"]
        }

        combo_event = ttk.Combobox(card, state="readonly")
        combo_event.pack(fill=tk.X, padx=25, pady=(0, 15), ipady=2)

        def update_event_options():
            cat = cat_var.get()
            opts = event_options.get(cat, [])
            combo_event['values'] = opts
            if opts: combo_event.set(opts[0])

        for cname in ["Sports", "Cultural", "Arts"]:
            rb = tk.Radiobutton(cat_frame, text=cname, value=cname, variable=cat_var, 
                                font=("Segoe UI", 9, "bold"), fg="#ffffff", bg="#1e293b", 
                                selectcolor="#2563eb", activebackground="#1e293b", 
                                command=update_event_options)
            rb.pack(side=tk.LEFT, padx=(0, 15))

        update_event_options()

        def submit_registration():
            name = entry_name.get().strip()
            dept = combo_dept.get().strip()
            uid = entry_uid.get().strip()
            email = entry_email.get().strip()
            category = cat_var.get()
            event_title = combo_event.get().strip()

            if not (name and dept and uid and email and event_title):
                messagebox.showwarning("Input Error", "Please fill in all registration fields.", parent=reg_win)
                return

            full_event_name = f"{category} Event: {event_title}"

            try:
                conn = sqlite3.connect(DB_PATH)
                cursor = conn.cursor()
                cursor.execute('''
                    INSERT INTO members (name, department, uid, email, event)
                    VALUES (?, ?, ?, ?, ?)
                ''', (name, dept, uid, email, full_event_name))
                conn.commit()
                new_id = cursor.lastrowid
                conn.close()

                messagebox.showinfo("Registration Successful", 
                                    f"Congratulations {name}!\n\n"
                                    f"Registration ID: #{new_id}\n"
                                    f"Event: {full_event_name}\n"
                                    f"UID: {uid} | Dept: {dept}\n\n"
                                    f"Registration recorded successfully in the club database!", 
                                    parent=reg_win)
                reg_win.destroy()
            except sqlite3.Error as e:
                messagebox.showerror("Database Error", f"Failed to record registration: {e}", parent=reg_win)

        btn_submit = tk.Button(reg_win, text="Confirm & Register for Event", font=("Segoe UI", 11, "bold"), bg="#10b981", fg="#ffffff", relief="flat", cursor="hand2", command=submit_registration)
        btn_submit.pack(fill=tk.X, padx=30, pady=(0, 20), ipady=5)

    # ==============================================================================
    # VIEW REGISTRATIONS WINDOW (TREEVIEW WITH SEARCH, FILTER, DELETE & EXPORT)
    # ==============================================================================
    def open_view_registration(self):
        view_win = tk.Toplevel()
        view_win.title("Registered Members Directory - Talent Enrichment Club")
        view_win.configure(bg="#0f172a")
        center_window(view_win, 1050, 680)

        # Header
        top = tk.Frame(view_win, bg="#1e293b", height=60)
        top.pack(fill=tk.X)
        tk.Label(top, text="REGISTERED MEMBERS DIRECTORY", font=("Segoe UI", 14, "bold"), fg="#ffffff", bg="#1e293b").pack(side=tk.LEFT, padx=20, pady=15)

        # Controls Strip
        ctrl_frame = tk.Frame(view_win, bg="#0f172a")
        ctrl_frame.pack(fill=tk.X, padx=20, pady=12)

        tk.Label(ctrl_frame, text="Search:", font=("Segoe UI", 9, "bold"), fg="#94a3b8", bg="#0f172a").pack(side=tk.LEFT, padx=(0, 5))
        search_entry = tk.Entry(ctrl_frame, font=("Segoe UI", 10), bg="#1e293b", fg="#ffffff", insertbackground="#ffffff", width=25)
        search_entry.pack(side=tk.LEFT, padx=(0, 15), ipady=3)

        tk.Label(ctrl_frame, text="Event Filter:", font=("Segoe UI", 9, "bold"), fg="#94a3b8", bg="#0f172a").pack(side=tk.LEFT, padx=(0, 5))
        filter_event = ttk.Combobox(ctrl_frame, values=["All", "Sports", "Cultural", "Arts"], state="readonly", width=12)
        filter_event.set("All")
        filter_event.pack(side=tk.LEFT, padx=(0, 15), ipady=2)

        # Table Frame
        table_frame = tk.Frame(view_win, bg="#1e293b")
        table_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=(0, 10))

        columns = ("ID", "Name", "Department", "UID", "Email", "Registered Event")
        tree = ttk.Treeview(table_frame, columns=columns, show="headings", selectmode="browse")
        
        tree.heading("ID", text="ID")
        tree.column("ID", width=50, anchor=tk.CENTER)

        tree.heading("Name", text="Member Name")
        tree.column("Name", width=180, anchor=tk.W)

        tree.heading("Department", text="Dept")
        tree.column("Department", width=70, anchor=tk.CENTER)

        tree.heading("UID", text="UID")
        tree.column("UID", width=110, anchor=tk.CENTER)

        tree.heading("Email", text="Email")
        tree.column("Email", width=180, anchor=tk.W)

        tree.heading("Registered Event", text="Registered Event")
        tree.column("Registered Event", width=250, anchor=tk.W)

        scrollbar = ttk.Scrollbar(table_frame, orient=tk.VERTICAL, command=tree.yview)
        tree.configure(yscroll=scrollbar.set)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        tree.pack(fill=tk.BOTH, expand=True)

        count_lbl = tk.Label(view_win, text="Loading members...", font=("Segoe UI", 9), fg="#64748b", bg="#0f172a")
        count_lbl.pack(anchor="w", padx=20, pady=(0, 10))

        def load_data():
            conn = sqlite3.connect(DB_PATH)
            c = conn.cursor()
            query = "SELECT id, name, department, uid, email, event FROM members WHERE 1=1"
            params = []

            s_text = search_entry.get().strip().lower()
            if s_text:
                query += " AND (LOWER(name) LIKE ? OR LOWER(uid) LIKE ? OR LOWER(email) LIKE ?)"
                params.extend([f"%{s_text}%", f"%{s_text}%", f"%{s_text}%"])

            ev_filt = filter_event.get()
            if ev_filt and ev_filt != "All":
                query += " AND event LIKE ?"
                params.append(f"%{ev_filt}%")

            query += " ORDER BY id DESC"
            rows = c.execute(query, params).fetchall()
            conn.close()

            tree.delete(*tree.get_children())
            for r in rows:
                tree.insert("", tk.END, values=r)

            count_lbl.config(text=f"Total Members Listed: {len(rows)}")

        search_entry.bind("<KeyRelease>", lambda e: load_data())
        filter_event.bind("<<ComboboxSelected>>", lambda e: load_data())

        # Action Buttons
        btn_frame = tk.Frame(view_win, bg="#0f172a")
        btn_frame.pack(fill=tk.X, padx=20, pady=(0, 15))

        def delete_selected():
            sel = tree.selection()
            if not sel:
                messagebox.showwarning("No Selection", "Please select a member row to delete.", parent=view_win)
                return

            item = tree.item(sel[0])
            mem_id = item['values'][0]
            mem_name = item['values'][1]

            if messagebox.askyesno("Confirm Delete", f"Are you sure you want to delete registration for '{mem_name}' (ID #{mem_id})?", parent=view_win):
                conn = sqlite3.connect(DB_PATH)
                c = conn.cursor()
                c.execute("DELETE FROM members WHERE id = ?", (mem_id,))
                conn.commit()
                conn.close()
                load_data()
                messagebox.showinfo("Deleted", f"Registration #{mem_id} removed successfully.", parent=view_win)

        def export_csv():
            file_path = filedialog.asksaveasfilename(
                parent=view_win,
                defaultextension=".csv",
                filetypes=[("CSV files", "*.csv"), ("All files", "*.*")],
                initialfile="Talent_Enrichment_Club_Members.csv"
            )
            if not file_path:
                return

            conn = sqlite3.connect(DB_PATH)
            c = conn.cursor()
            rows = c.execute("SELECT id, name, department, uid, email, event FROM members ORDER BY id ASC").fetchall()
            conn.close()

            try:
                with open(file_path, "w", newline="", encoding="utf-8") as f:
                    writer = csv.writer(f)
                    writer.writerow(["ID", "Name", "Department", "UID", "Email", "Event"])
                    writer.writerows(rows)
                messagebox.showinfo("Export Successful", f"Saved {len(rows)} records to:\n{file_path}", parent=view_win)
            except Exception as e:
                messagebox.showerror("Export Failed", f"Error saving file: {e}", parent=view_win)

        tk.Button(btn_frame, text="Delete Selected", font=("Segoe UI", 9, "bold"), bg="#ef4444", fg="#ffffff", relief="flat", cursor="hand2", command=delete_selected).pack(side=tk.LEFT, padx=(0, 10))
        tk.Button(btn_frame, text="Export CSV", font=("Segoe UI", 9, "bold"), bg="#2563eb", fg="#ffffff", relief="flat", cursor="hand2", command=export_csv).pack(side=tk.LEFT, padx=(0, 10))
        tk.Button(btn_frame, text="Refresh", font=("Segoe UI", 9, "bold"), bg="#334155", fg="#ffffff", relief="flat", cursor="hand2", command=load_data).pack(side=tk.LEFT)

        load_data()

    # ==============================================================================
    # VIEW MEMBERS BY EVENT WINDOW
    # ==============================================================================
    def open_event_view_window(self):
        ev_win = tk.Toplevel()
        ev_win.title("View Members by Specific Event - Talent Enrichment Club")
        ev_win.configure(bg="#0f172a")
        center_window(ev_win, 800, 600)

        tk.Label(ev_win, text="VIEW REGISTERED MEMBERS BY EVENT", font=("Segoe UI", 15, "bold"), fg="#60a5fa", bg="#0f172a").pack(pady=(15, 10))

        filter_card = tk.Frame(ev_win, bg="#1e293b", bd=1, relief="solid")
        filter_card.pack(fill=tk.X, padx=25, pady=10)

        # Sports Events Dropdown
        tk.Label(filter_card, text="Sports Events:", font=("Segoe UI", 9, "bold"), fg="#38bdf8", bg="#1e293b").grid(row=0, column=0, padx=15, pady=8, sticky="w")
        cb_sports = ttk.Combobox(filter_card, values=["Cricket Championship", "Football League", "Badminton Masters", "Basketball Shootout", "Kabaddi Warriors", "Table Tennis Open"], state="readonly", width=28)
        cb_sports.grid(row=0, column=1, padx=15, pady=8)

        # Cultural Events Dropdown
        tk.Label(filter_card, text="Cultural Events:", font=("Segoe UI", 9, "bold"), fg="#c084fc", bg="#1e293b").grid(row=1, column=0, padx=15, pady=8, sticky="w")
        cb_cultural = ttk.Combobox(filter_card, values=["Vocal & Instrumental Music", "Choreography & Dance", "Skits & Theatrical Drama", "Standup Comedy Night"], state="readonly", width=28)
        cb_cultural.grid(row=1, column=1, padx=15, pady=8)

        # Arts Events Dropdown
        tk.Label(filter_card, text="Arts Events:", font=("Segoe UI", 9, "bold"), fg="#fbbf24", bg="#1e293b").grid(row=2, column=0, padx=15, pady=8, sticky="w")
        cb_arts = ttk.Combobox(filter_card, values=["Canvas Oil & Watercolor Painting", "Pencil Sketching & Caricature", "Digital Illustration & Design"], state="readonly", width=28)
        cb_arts.grid(row=2, column=1, padx=15, pady=8)

        # Listbox for registered members
        list_frame = tk.Frame(ev_win, bg="#1e293b")
        list_frame.pack(fill=tk.BOTH, expand=True, padx=25, pady=10)

        listbox = tk.Listbox(list_frame, font=("Segoe UI", 10), bg="#0f172a", fg="#ffffff", selectbackground="#2563eb", bd=1, relief="solid")
        scroll = ttk.Scrollbar(list_frame, orient=tk.VERTICAL, command=listbox.yview)
        listbox.config(yscrollcommand=scroll.set)
        scroll.pack(side=tk.RIGHT, fill=tk.Y)
        listbox.pack(fill=tk.BOTH, expand=True)

        count_lbl = tk.Label(ev_win, text="Select an event from any category above to view attendees.", font=("Segoe UI", 9), fg="#94a3b8", bg="#0f172a")
        count_lbl.pack(pady=(0, 10))

        def fetch_members_for_event(event_name):
            listbox.delete(0, tk.END)
            conn = sqlite3.connect(DB_PATH)
            c = conn.cursor()
            rows = c.execute("SELECT id, name, department, uid, email FROM members WHERE event LIKE ?", (f"%{event_name}%",)).fetchall()
            conn.close()

            if rows:
                for idx, r in enumerate(rows, 1):
                    listbox.insert(tk.END, f"  {idx}. {r[1]}  |  Dept: {r[2]}  |  UID: {r[3]}  |  Email: {r[4]}")
                count_lbl.config(text=f"Enrolled in {event_name}: {len(rows)} student(s)")
            else:
                listbox.insert(tk.END, "  No students registered for this event yet.")
                count_lbl.config(text=f"No registrations found for: {event_name}")

        cb_sports.bind("<<ComboboxSelected>>", lambda e: fetch_members_for_event(cb_sports.get()))
        cb_cultural.bind("<<ComboboxSelected>>", lambda e: fetch_members_for_event(cb_cultural.get()))
        cb_arts.bind("<<ComboboxSelected>>", lambda e: fetch_members_for_event(cb_arts.get()))

    # ==============================================================================
    # MANAGE EVENTS WINDOW (ADMIN CAN ADD & LIST EVENTS)
    # ==============================================================================
    def open_manage_events(self):
        me_win = tk.Toplevel()
        me_win.title("Manage Club Events - Talent Enrichment Club")
        me_win.configure(bg="#0f172a")
        center_window(me_win, 800, 650)

        tk.Label(me_win, text="MANAGE CLUB EVENTS", font=("Segoe UI", 15, "bold"), fg="#60a5fa", bg="#0f172a").pack(pady=(15, 10))

        add_frame = tk.Frame(me_win, bg="#1e293b", bd=1, relief="solid")
        add_frame.pack(fill=tk.X, padx=25, pady=10)

        tk.Label(add_frame, text="Event Title:", font=("Segoe UI", 9, "bold"), fg="#ffffff", bg="#1e293b").grid(row=0, column=0, padx=10, pady=5, sticky="w")
        ent_title = tk.Entry(add_frame, font=("Segoe UI", 10), bg="#0f172a", fg="#ffffff", insertbackground="#ffffff")
        ent_title.grid(row=0, column=1, padx=10, pady=5, sticky="ew")

        tk.Label(add_frame, text="Category:", font=("Segoe UI", 9, "bold"), fg="#ffffff", bg="#1e293b").grid(row=0, column=2, padx=10, pady=5, sticky="w")
        combo_cat = ttk.Combobox(add_frame, values=["Sports", "Cultural", "Arts"], state="readonly", width=12)
        combo_cat.set("Sports")
        combo_cat.grid(row=0, column=3, padx=10, pady=5)

        tk.Label(add_frame, text="Venue:", font=("Segoe UI", 9, "bold"), fg="#ffffff", bg="#1e293b").grid(row=1, column=0, padx=10, pady=5, sticky="w")
        ent_venue = tk.Entry(add_frame, font=("Segoe UI", 10), bg="#0f172a", fg="#ffffff", insertbackground="#ffffff")
        ent_venue.grid(row=1, column=1, padx=10, pady=5, sticky="ew")

        tk.Label(add_frame, text="Max Seats:", font=("Segoe UI", 9, "bold"), fg="#ffffff", bg="#1e293b").grid(row=1, column=2, padx=10, pady=5, sticky="w")
        ent_seats = tk.Entry(add_frame, font=("Segoe UI", 10), bg="#0f172a", fg="#ffffff", insertbackground="#ffffff", width=12)
        ent_seats.insert(0, "50")
        ent_seats.grid(row=1, column=3, padx=10, pady=5)

        add_frame.grid_columnconfigure(1, weight=1)

        # Existing Events Treeview
        tree_frame = tk.Frame(me_win, bg="#1e293b")
        tree_frame.pack(fill=tk.BOTH, expand=True, padx=25, pady=10)

        tree = ttk.Treeview(tree_frame, columns=("ID", "Title", "Category", "Venue", "Seats"), show="headings")
        tree.heading("ID", text="ID"); tree.column("ID", width=40, anchor=tk.CENTER)
        tree.heading("Title", text="Title"); tree.column("Title", width=220, anchor=tk.W)
        tree.heading("Category", text="Category"); tree.column("Category", width=90, anchor=tk.CENTER)
        tree.heading("Venue", text="Venue"); tree.column("Venue", width=180, anchor=tk.W)
        tree.heading("Seats", text="Max Seats"); tree.column("Seats", width=70, anchor=tk.CENTER)

        tree.pack(fill=tk.BOTH, expand=True)

        def refresh_events():
            conn = sqlite3.connect(DB_PATH)
            c = conn.cursor()
            rows = c.execute("SELECT id, title, category, venue, max_seats FROM events ORDER BY id DESC").fetchall()
            conn.close()
            tree.delete(*tree.get_children())
            for r in rows:
                tree.insert("", tk.END, values=r)

        def save_event():
            title = ent_title.get().strip()
            cat = combo_cat.get()
            venue = ent_venue.get().strip()
            seats = ent_seats.get().strip()

            if not title or not venue:
                messagebox.showwarning("Warning", "Title and Venue are required.", parent=me_win)
                return

            try:
                conn = sqlite3.connect(DB_PATH)
                c = conn.cursor()
                c.execute('''
                    INSERT INTO events (title, category, venue, max_seats)
                    VALUES (?, ?, ?, ?)
                ''', (title, cat, venue, int(seats) if seats.isdigit() else 50))
                conn.commit()
                conn.close()
                ent_title.delete(0, tk.END)
                ent_venue.delete(0, tk.END)
                refresh_events()
                messagebox.showinfo("Success", f"Event '{title}' created successfully!", parent=me_win)
            except Exception as e:
                messagebox.showerror("Error", f"Failed to add event: {e}", parent=me_win)

        tk.Button(add_frame, text="+ Add Event", font=("Segoe UI", 9, "bold"), bg="#10b981", fg="#ffffff", relief="flat", cursor="hand2", command=save_event).grid(row=2, column=3, padx=10, pady=8, sticky="e")

        refresh_events()

# Entry Point
if __name__ == "__main__":
    root = tk.Tk()
    app = TalentClubApp(root)
    root.mainloop()
