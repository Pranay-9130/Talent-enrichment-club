import tkinter as tk
from tkinter import messagebox
from tkinter import ttk
import sqlite3
from tkinter import *

# Global dictionary to hold member details
member_info = {}

# Connect to SQLite database (it will create the database if it doesn't exist)
conn = sqlite3.connect('talent_enrichment_club.db')
cursor = conn.cursor()

# Add the event column if it doesn't exist
try:
    cursor.execute("ALTER TABLE members ADD COLUMN event TEXT")
except sqlite3.OperationalError:
    # Ignore the error if the column already exists
    pass

# Create the members table if it doesn't exist
cursor.execute('''
    CREATE TABLE IF NOT EXISTS members (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT,
        department TEXT,
        uid TEXT,
        email TEXT,
        event TEXT
    )
''')

# Commit the changes and close the connection
conn.commit()
conn.close()

def register_member():
    # Get the values entered by the user
    name = entry_name.get()
    department = department_combobox.get()
    uid = entry_uid.get()
    email = entry_email.get()

    # Check if all fields are filled
    if name and department and uid and email:
        try:
            # Store the member's information in the global dictionary
            member_info['name'] = name
            member_info['department'] = department
            member_info['uid'] = uid
            member_info['email'] = email
            
            # Connect to the SQLite database and insert data
            conn = sqlite3.connect('talent_enrichment_club.db')
            cursor = conn.cursor()
            cursor.execute('''INSERT INTO members (name, department, uid, email) VALUES (?, ?, ?, ?)''',
                           (name, department, uid, email))
            conn.commit()
            conn.close()

            # Show success message
            messagebox.showinfo("Success", "Member Registered Successfully!")
            clear_fields()

            # After successful registration, proceed to the event registration screen
            open_event_registration_window()  # Opens the event registration screen
        except sqlite3.Error as e:
            # In case of any database errors, show an error message
            messagebox.showerror("Database Error", f"An error occurred: {e}")
    else:
        messagebox.showwarning("Input Error", "Please fill all fields.")

def show_members():
    # Fetch all members from the database
    conn = sqlite3.connect('talent_enrichment_club.db')
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM members")
    members = cursor.fetchall()
    conn.close()

   

def clear_fields():
    # Clear the input fields
    entry_name.delete(0, tk.END)
    department_combobox.set('')  # Reset dropdown
    entry_uid.delete(0, tk.END)
    entry_email.delete(0, tk.END)

def login():
    username = entry_username.get()
    password = entry_password.get()

    # Basic validation for login (you can add a more robust system later)
    if username == "1" and password == "1":  # Change this to a secure validation later
        login_window.destroy()  # Close the login window
        open_dashboard_window()  # Open the dashboard window
    else:
        messagebox.showerror("Login Failed", "Incorrect username or password")

def open_dashboard_window():
    # Setting up the Tkinter window for the dashboard
    dashboard_window = tk.Tk()
    dashboard_window.title("Dashboard")
    dashboard_window.geometry("1560x1000")

    # Creating the heading for the university
    label_heading = tk.Label(dashboard_window, text="AURORA DEEMED TO BE UNIVERSITY", font=("Times new roman", 26, "bold"),fg="red")
    label_heading.pack(pady=20)
    Label_subheading = tk.Label(dashboard_window, text="WELCOME TO TALENT ENRICHMENT CLUB", font=("Times new roman", 20, "bold"),fg="blue")
    Label_subheading.pack(pady=30)

    # Creating buttons for the dashboard
    button_registration = tk.Button(dashboard_window, text="Registration",font=("times new roman",14,"bold"),bg="#ff9800",fg="black",activebackground="#fb8c00",activeforeground="white" ,command=open_registration_window)
    button_registration.pack(padx=15,pady=30)

    view_button = tk.Button(dashboard_window, text="View Registered Members",font=("times new roman",14,"bold"),bg="#ff9800",fg="black", activebackground="#fb8c00",activeforeground="white" ,command=open_view_registration)
    view_button.pack(padx=15,pady=30)

    button_manage_events = tk.Button(dashboard_window, text="Manage Events",font=("times new roman",14,"bold"),bg="#ff9800",fg="black", activebackground="#fb8c00",activeforeground="white" , command=manage_events)
    button_manage_events.pack(padx=15,pady=30)

    # Add a button for viewing members by event
    button_view_event = tk.Button(dashboard_window, text="View Members by Event",font=("times new roman",14,"bold"),bg="#ff9800",fg="black", activebackground="#fb8c00",activeforeground="white" , command=open_event_view_window)
    button_view_event.pack(padx=15,pady=30)

    # Start the Tkinter event loop for the dashboard window
    dashboard_window.mainloop()

def open_view_registration():
    # Setting up the Tkinter window for viewing registrations
    view_window = tk.Toplevel()
    view_window.title("View Registrations")
    view_window.geometry("1560x1000")

    # Create a Treeview widget for the table
    columns = ("ID", "Name", "Event", "Department")
    tree = ttk.Treeview(view_window, columns=columns, show="headings", height=10)
    tree.pack(pady=10, fill=tk.BOTH, expand=True)

    # Define column headings and their width
    for col in columns:
        tree.heading(col, text=col)
        tree.column(col, width=250, anchor=tk.CENTER)

    def show_members():
        # Fetch and display registered members from the database
        conn = sqlite3.connect('talent_enrichment_club.db')
        cursor = conn.cursor()
        cursor.execute("SELECT rowid, name, event, department FROM members")
        members = cursor.fetchall()
        conn.close()

        # Clear the table before adding new items
        for item in tree.get_children():
            tree.delete(item)

        # Insert each member as a row in the table
        for member in members:
            tree.insert("", tk.END, values=(member[0], member[1], member[2], member[3]))

    def delete_registration():
        # Get the selected item from the table
        selected_item = tree.selection()
        if not selected_item:
            messagebox.showwarning("No Selection", "Please select a registration to delete.")
            return

        # Extract the ID of the selected registration
        member_id = tree.item(selected_item, "values")[0]

        # Confirm deletion
        confirm = messagebox.askyesno("Confirm Deletion", f"Are you sure you want to delete registration ID {member_id}?")
        if confirm:
            # Delete the registration from the database
            conn = sqlite3.connect('talent_enrichment_club.db')
            cursor = conn.cursor()
            cursor.execute("DELETE FROM members WHERE rowid = ?", (member_id,))
            conn.commit()
            conn.close()

            # Update the table
            show_members()
            messagebox.showinfo("Deleted", f"Registration ID {member_id} has been deleted.")

    # Button to delete the selected registration
    delete_button = tk.Button(view_window, text="Delete Registration", font=("times new roman", 16, "bold"),
                              bg="red", fg="white", command=delete_registration)
    delete_button.pack(pady=10)

    # Initially populate the table
    show_members()




def open_registration_window():
    # Setting up the Tkinter window for the registration form
    registration_window = tk.Tk()
    registration_window.title("Registration Form")
    registration_window.geometry("1560x1000")
    label_heading = tk.Label(registration_window, text="STUDENT REGISTRATION FORM", font=("times new roman", 26, "bold"))
    label_heading.pack(pady=20)

    label_name = tk.Label(registration_window, text="Name:",font=("times new roman",20,"bold"),fg="black")
    label_name.pack(pady=20)
    global entry_name
    entry_name = tk.Entry(registration_window,width=30,font=("times new roman",18),bd=3,relief="solid")
    entry_name.pack(pady=5)

    label_department = tk.Label(registration_window, text="Department:",font=("times new roman",20,"bold"),fg="black")
    label_department.pack(pady=20)
    global department_combobox
    department_combobox = ttk.Combobox(registration_window, 
                                       values=["CSE", "AIML", "DS", "BBA", "BCA", "MCA", "MBA"], 
                                       state="readonly")
    department_combobox.pack(pady=5)

    label_uid = tk.Label(registration_window, text="UID:",font=("times new roman",20,"bold"),fg="black")
    label_uid.pack(pady=20)
    global entry_uid
    entry_uid = tk.Entry(registration_window,width=30,font=("times new roman",18),bd=3,relief="solid")
    entry_uid.pack(pady=5)

    label_email = tk.Label(registration_window, text="Email:",font=("times new roman",20,"bold"),fg="black")
    label_email.pack(pady=20)
    global entry_email
    entry_email = tk.Entry(registration_window,width=30,font=("times new roman",18),bd=3,relief="solid")
    entry_email.pack(pady=5)

    button_next = tk.Button(registration_window, text="Next",font=("times new roman",16,"bold"),bg="brown",fg="white", command=register_member)
    button_next.pack(pady=10)

    registration_window.mainloop()

def open_event_registration_window():
    # Setting up the Tkinter window for the event registration form
    events_window = tk.Tk()
    events_window.title("Events")
    events_window.geometry("1560x1000")
    events_window.config(bg="lightyellow")  # Set background color of the window

    # Heading label with custom colors
    label_events_heading = tk.Label(events_window, 
                                    text="Select an Event Category", 
                                    font=("Times new roman", 26, "bold"), 
                                    fg="green", 
                                    bg="lightyellow")
    label_events_heading.pack(pady=20)

    global sports_combobox, cultural_combobox, arts_combobox

    # Sports events label and combobox with custom colors
    label_sports = tk.Label(events_window, text="Sports Events:", font=("Times new roman", 16, "bold"), fg="blue", bg="lightyellow")
    label_sports.pack(pady=15)
    sports_combobox = ttk.Combobox(events_window, 
                                    values=["Cricket", "Kabaddi", "Badminton", "Volleyball", "Basketball", "Football", "Table Tennis"],
                                    state="readonly", width=35, style="TCombobox")
    sports_combobox.pack(pady=15)

    # Cultural events label and combobox with custom colors
    label_cultural = tk.Label(events_window, text="Cultural Events:", font=("Times new roman", 16, "bold"), fg="purple", bg="lightyellow")
    label_cultural.pack(pady=15)
    cultural_combobox = ttk.Combobox(events_window, 
                                      values=["--select--", "Music", "Dance", "Skits", "Standup Comedy"],
                                      state="readonly", width=35, style="TCombobox")
    cultural_combobox.pack(pady=15)

    # Arts events label and combobox with custom colors
    label_arts = tk.Label(events_window, text="Arts Events:", font=("Times new roman", 16, "bold"), fg="red", bg="lightyellow")
    label_arts.pack(pady=15)
    arts_combobox = ttk.Combobox(events_window, 
                                  values=["Painting", "Sketching"],
                                  state="readonly", width=35, style="TCombobox")
    arts_combobox.pack(pady=15)

    # Register button with custom text and background colors
    button_register = tk.Button(events_window, text="Register", font=("times new roman", 20, "bold"), fg="white", bg="blue", command=register_for_event)
    button_register.pack(pady=10)

    events_window.mainloop()

def open_event_view_window():
    event_view_window = tk.Tk()
    event_view_window.title("View Members by Event")
    event_view_window.geometry("1400x1100")  # Set a fixed size, or use 'event_view_window.geometry("fullscreen")' for full screen
    event_view_window.config(bg="lightcyan")  # Set background color of the window

    # Heading label with custom colors
    label_heading = tk.Label(event_view_window, 
                             text="Select Event to View Registrations", 
                             font=("Arial", 16, "bold"), 
                             fg="darkblue", 
                             bg="lightcyan")
    label_heading.grid(row=0, column=0, columnspan=3, pady=20)

    # Sports Events label and dropdown with custom colors
    label_sports = tk.Label(event_view_window, text="Sports Events:", font=("Arial", 12, "bold"), fg="blue", bg="lightcyan")
    label_sports.grid(row=1, column=0, padx=10, pady=10, sticky="w")
    sports_dropdown = ttk.Combobox(event_view_window, 
                                    values=["Cricket", "Kabaddi", "Badminton", "Volleyball", "Basketball", "Football", "Table Tennis"],
                                    state="readonly", width=35)
    sports_dropdown.grid(row=1, column=1, padx=10, pady=10)

    # Cultural Events label and dropdown with custom colors
    label_cultural = tk.Label(event_view_window, text="Cultural Events:", font=("Arial", 12, "bold"), fg="purple", bg="lightcyan")
    label_cultural.grid(row=2, column=0, padx=10, pady=10, sticky="w")
    cultural_dropdown = ttk.Combobox(event_view_window, 
                                      values=["Music", "Dance", "Skits", "Standup Comedy"],
                                      state="readonly", width=35)
    cultural_dropdown.grid(row=2, column=1, padx=10, pady=10)

    # Arts Events label and dropdown with custom colors
    label_arts = tk.Label(event_view_window, text="Arts Events:", font=("Arial", 12, "bold"), fg="green", bg="lightcyan")
    label_arts.grid(row=3, column=0, padx=10, pady=10, sticky="w")
    arts_dropdown = ttk.Combobox(event_view_window, 
                                  values=["Painting", "Sketching"],
                                  state="readonly", width=35)
    arts_dropdown.grid(row=3, column=1, padx=10, pady=10)

    # Listbox for displaying members
    global listbox_event_members
    listbox_event_members = tk.Listbox(event_view_window, width=80, height=20, bg="lightyellow", fg="darkblue")
    listbox_event_members.grid(row=4, column=0, columnspan=3, pady=20)

    # Function to fetch and display members based on selected event
    def fetch_members_by_event():
        listbox_event_members.delete(0, tk.END)
        selected_event = None
        if sports_dropdown.get():
            selected_event = f"Sports Event: {sports_dropdown.get()}"
        elif cultural_dropdown.get():
            selected_event = f"Cultural Event: {cultural_dropdown.get()}"
        elif arts_dropdown.get():
            selected_event = f"Arts Event: {arts_dropdown.get()}"

        if selected_event:
            conn = sqlite3.connect('talent_enrichment_club.db')
            cursor = conn.cursor()
            cursor.execute("SELECT name, department FROM members WHERE event LIKE ?", (f"%{selected_event}%",))
            members = cursor.fetchall()
            conn.close()

            if members:
                for member in members:
                    listbox_event_members.insert(tk.END, f"{member[0]} - {member[1]}")
            else:
                listbox_event_members.insert(tk.END, "No members registered for this event.")
        else:
            messagebox.showwarning("Select Event", "Please select an event to view members.")

    # Button with custom colors and positioning
    button_fetch_members = tk.Button(event_view_window, 
                                     text="View Members", 
                                     font=("Arial", 14, "bold"), 
                                     fg="white", 
                                     bg="darkgreen", 
                                     command=fetch_members_by_event)
    button_fetch_members.grid(row=5, column=0, columnspan=3, pady=10)

    event_view_window.mainloop()


def manage_events():
    messagebox.showinfo("Manage Events", "This feature will be implemented soon.")



# Setting up the Tkinter window for the login form
login_window = tk.Tk()
login_window.title("Login")
login_window.geometry("1400x1100")  # Optimized window size
login_window.configure(bg="#f0f8ff")  # Light blue background

# Adding the heading with a custom font and color
label_heading = tk.Label(
    login_window,
    text="AURORA DEEMED TO BE UNIVERSITY",
    font=("Times New Roman", 24, "bold"),
    fg="#2b5797",  # Dark blue text
    bg="#f0f8ff",
    padx=140
)
label_heading.place(x=250, y=30)  # Center-aligned heading

# Username label and entry
login_image = PhotoImage(file="login.png")
label_username = tk.Label(
    login_window,
    image=login_image,
    compound="left",
    text="Username:",
    font=("Times New Roman", 18, "bold"),
    fg="#444444",  # Dark gray text
    bg="#f0f8ff",
)
label_username.place(x=420, y=100)

entry_username = tk.Entry(
    login_window,
    font=("Arial", 16),
    width=25,
    bd=3,
    relief="solid"
)
entry_username.place(x=560, y=110)

# Password label and entry
password_image = PhotoImage(file="password.png")
label_password = tk.Label(
    login_window,
    text="Password:",
    image=password_image,
    compound="left",
    font=("Times New Roman", 18, "bold"),
    fg="#444444",
    bg="#f0f8ff"
)
label_password.place(x=420, y=190)

entry_password = tk.Entry(
    login_window,
    font=("Arial", 16),
    show="*",
    width=25,
    bd=3,
    relief="solid"
)
entry_password.place(x=560, y=190)

# Adding a styled login button
button_login = tk.Button(
    login_window,
    text="Login",
    command=login,
    font=("Arial", 16, "bold"),
    bg="#4caf50",  # Green background
    fg="white",  # White text
    activebackground="#45a049",  # Darker green when pressed
    activeforeground="white",  # Keep text white when pressed
    bd=2,
    relief="raised",
    padx=10
)
button_login.place(x=600, y=270)

# Adding the sports image at the bottom
sports_image = PhotoImage(file="Sports1.png")
sports_img_label = tk.Label(
    login_window,
    image=sports_image,
    bg="#f0f8ff"
)
sports_img_label.place(x=350, y=350)

login_window.mainloop()

