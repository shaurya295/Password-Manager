# ============================================================
# Password Manager - APP Course End Semester Project
# Built with: Python, Tkinter (GUI), SQLite3 (Database)
# ============================================================

import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3
import hashlib
import base64
import string
import random
import os

# ============================================================
# DATABASE SETUP
# ============================================================

def get_db_path():
    """Returns the path for the database file (same folder as this script)."""
    folder = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(folder, "passwords.db")

def init_database():
    """Creates the database and tables if they don't already exist."""
    conn = sqlite3.connect(get_db_path())
    cursor = conn.cursor()

    # Table to store the master password hash
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS master (
            id INTEGER PRIMARY KEY,
            password_hash TEXT NOT NULL
        )
    """)

    # Table to store saved passwords
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS passwords (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            website TEXT NOT NULL,
            username TEXT NOT NULL,
            password TEXT NOT NULL
        )
    """)

    conn.commit()
    conn.close()

# ============================================================
# HELPER FUNCTIONS
# ============================================================

def hash_password(password):
    """
    Hashes a password using SHA-256 for secure storage.
    We never store the master password in plain text.
    """
    return hashlib.sha256(password.encode()).hexdigest()

def encode_password(password):
    """
    Encodes a password using Base64 before storing in the database.
    This is a simple encoding so passwords aren't stored as plain text.
    """
    return base64.b64encode(password.encode()).decode()

def decode_password(encoded_password):
    """
    Decodes a Base64-encoded password back to its original form.
    """
    return base64.b64decode(encoded_password.encode()).decode()

def generate_random_password(length=12):
    """
    Generates a random password with uppercase, lowercase, digits, and symbols.
    """
    characters = string.ascii_letters + string.digits + "!@#$%&*"
    password = ''.join(random.choice(characters) for _ in range(length))
    return password

# ============================================================
# MAIN APPLICATION CLASS
# ============================================================

class PasswordManagerApp:
    """Main application class that manages all the screens and logic."""

    def __init__(self, root):
        self.root = root
        self.root.title("Password Manager")
        self.root.geometry("750x520")
        self.root.resizable(False, False)
        self.root.configure(bg="#f0f4f8")

        # Initialize the database
        init_database()

        # Set a consistent style for ttk widgets
        self.style = ttk.Style()
        self.style.theme_use("clam")
        self.style.configure("TButton", font=("Segoe UI", 10), padding=6)
        self.style.configure("TLabel", font=("Segoe UI", 11), background="#f0f4f8")
        self.style.configure("Header.TLabel", font=("Segoe UI", 18, "bold"), background="#f0f4f8")
        self.style.configure("TEntry", font=("Segoe UI", 11), padding=5)

        # Check if master password exists to show the right screen
        if self.is_master_password_set():
            self.show_login_screen()
        else:
            self.show_setup_screen()

    # ---------- Utility ----------

    def clear_screen(self):
        """Removes all widgets from the window to show a new screen."""
        for widget in self.root.winfo_children():
            widget.destroy()

    def is_master_password_set(self):
        """Checks if a master password has been set already."""
        conn = sqlite3.connect(get_db_path())
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM master")
        count = cursor.fetchone()[0]
        conn.close()
        return count > 0

    # ============================================================
    # SCREEN 1: FIRST-TIME SETUP (Set Master Password)
    # ============================================================

    def show_setup_screen(self):
        """Shows the screen where user sets the master password for the first time."""
        self.clear_screen()

        frame = tk.Frame(self.root, bg="#f0f4f8")
        frame.place(relx=0.5, rely=0.5, anchor="center")

        ttk.Label(frame, text="🔐 Set Master Password", style="Header.TLabel").pack(pady=(0, 10))
        ttk.Label(frame, text="This password will be used to access your vault.").pack(pady=(0, 20))

        ttk.Label(frame, text="Enter Password:").pack(anchor="w", padx=5)
        self.setup_pass = ttk.Entry(frame, show="*", width=35)
        self.setup_pass.pack(pady=(0, 10), ipady=4)

        ttk.Label(frame, text="Confirm Password:").pack(anchor="w", padx=5)
        self.setup_confirm = ttk.Entry(frame, show="*", width=35)
        self.setup_confirm.pack(pady=(0, 20), ipady=4)

        # Button with event handler
        ttk.Button(frame, text="Set Password", command=self.set_master_password).pack(ipadx=20, ipady=4)

        # Bind Enter key as well
        self.root.bind("<Return>", lambda event: self.set_master_password())
        self.setup_pass.focus()

    def set_master_password(self):
        """Event handler: validates and saves the master password."""
        password = self.setup_pass.get()
        confirm = self.setup_confirm.get()

        if len(password) < 4:
            messagebox.showwarning("Weak Password", "Password must be at least 4 characters long.")
            return
        if password != confirm:
            messagebox.showerror("Mismatch", "Passwords do not match. Please try again.")
            return

        # Store the hashed password in the database
        hashed = hash_password(password)
        conn = sqlite3.connect(get_db_path())
        cursor = conn.cursor()
        cursor.execute("INSERT INTO master (password_hash) VALUES (?)", (hashed,))
        conn.commit()
        conn.close()

        messagebox.showinfo("Success", "Master password set successfully!")
        self.root.unbind("<Return>")
        self.show_login_screen()

    # ============================================================
    # SCREEN 2: LOGIN SCREEN
    # ============================================================

    def show_login_screen(self):
        """Shows the login screen where user enters the master password."""
        self.clear_screen()

        frame = tk.Frame(self.root, bg="#f0f4f8")
        frame.place(relx=0.5, rely=0.5, anchor="center")

        ttk.Label(frame, text="🔒 Password Manager", style="Header.TLabel").pack(pady=(0, 10))
        ttk.Label(frame, text="Enter your master password to continue.").pack(pady=(0, 20))

        ttk.Label(frame, text="Master Password:").pack(anchor="w", padx=5)
        self.login_pass = ttk.Entry(frame, show="*", width=35)
        self.login_pass.pack(pady=(0, 20), ipady=4)

        ttk.Button(frame, text="Unlock", command=self.verify_login).pack(ipadx=30, ipady=4)

        # Bind Enter key for quick login
        self.root.bind("<Return>", lambda event: self.verify_login())
        self.login_pass.focus()

    def verify_login(self):
        """Event handler: checks if the entered master password is correct."""
        entered = self.login_pass.get()
        hashed = hash_password(entered)

        conn = sqlite3.connect(get_db_path())
        cursor = conn.cursor()
        cursor.execute("SELECT password_hash FROM master WHERE id=1")
        stored_hash = cursor.fetchone()[0]
        conn.close()

        if hashed == stored_hash:
            self.root.unbind("<Return>")
            self.show_dashboard()
        else:
            messagebox.showerror("Access Denied", "Incorrect master password!")
            self.login_pass.delete(0, tk.END)

    # ============================================================
    # SCREEN 3: MAIN DASHBOARD
    # ============================================================

    def show_dashboard(self):
        """Shows the main dashboard after successful login."""
        self.clear_screen()

        # --- Top Bar ---
        top_frame = tk.Frame(self.root, bg="#2c3e50", height=60)
        top_frame.pack(fill="x")
        top_frame.pack_propagate(False)

        tk.Label(
            top_frame, text="🔐 Password Manager", font=("Segoe UI", 16, "bold"),
            fg="white", bg="#2c3e50"
        ).pack(side="left", padx=20)

        tk.Button(
            top_frame, text="🚪 Logout", font=("Segoe UI", 10),
            bg="#e74c3c", fg="white", relief="flat", cursor="hand2",
            command=self.show_login_screen
        ).pack(side="right", padx=20, pady=15)

        # --- Content Area ---
        content = tk.Frame(self.root, bg="#f0f4f8")
        content.pack(fill="both", expand=True, padx=20, pady=15)

        # --- Left Panel: Add Password Form ---
        left = tk.LabelFrame(content, text=" Add New Password ", font=("Segoe UI", 11, "bold"),
                             bg="#ffffff", padx=15, pady=15)
        left.pack(side="left", fill="both", expand=True, padx=(0, 10))

        # Website field
        ttk.Label(left, text="Website:", background="#ffffff").pack(anchor="w")
        self.entry_website = ttk.Entry(left, width=28)
        self.entry_website.pack(fill="x", pady=(0, 8), ipady=3)

        # Username field
        ttk.Label(left, text="Username / Email:", background="#ffffff").pack(anchor="w")
        self.entry_username = ttk.Entry(left, width=28)
        self.entry_username.pack(fill="x", pady=(0, 8), ipady=3)

        # Password field
        ttk.Label(left, text="Password:", background="#ffffff").pack(anchor="w")
        self.entry_password = ttk.Entry(left, width=28)
        self.entry_password.pack(fill="x", pady=(0, 5), ipady=3)

        # Generate password button
        ttk.Button(left, text="🎲 Generate Password", command=self.fill_generated_password).pack(fill="x", pady=(0, 10))

        # Save button
        save_btn = tk.Button(
            left, text="💾  Save Password", font=("Segoe UI", 11, "bold"),
            bg="#27ae60", fg="white", relief="flat", cursor="hand2",
            command=self.save_password
        )
        save_btn.pack(fill="x", ipady=6)

        # --- Right Panel: Saved Passwords ---
        right = tk.LabelFrame(content, text=" Saved Passwords ", font=("Segoe UI", 11, "bold"),
                              bg="#ffffff", padx=10, pady=10)
        right.pack(side="right", fill="both", expand=True, padx=(10, 0))

        # Search bar
        search_frame = tk.Frame(right, bg="#ffffff")
        search_frame.pack(fill="x", pady=(0, 8))

        self.search_var = tk.StringVar()
        search_entry = ttk.Entry(search_frame, textvariable=self.search_var, width=20)
        search_entry.pack(side="left", fill="x", expand=True, ipady=3)

        ttk.Button(search_frame, text="🔍 Search", command=self.search_passwords).pack(side="left", padx=(5, 0))
        ttk.Button(search_frame, text="↻ All", command=self.load_passwords).pack(side="left", padx=(5, 0))

        # Bind key event: search as you type
        self.search_var.trace_add("write", lambda *args: self.search_passwords())

        # Treeview (table) to display passwords
        columns = ("website", "username", "password")
        self.tree = ttk.Treeview(right, columns=columns, show="headings", height=10)
        self.tree.heading("website", text="Website")
        self.tree.heading("username", text="Username")
        self.tree.heading("password", text="Password")
        self.tree.column("website", width=110)
        self.tree.column("username", width=110)
        self.tree.column("password", width=110)
        self.tree.pack(fill="both", expand=True)

        # Scrollbar for the table
        scrollbar = ttk.Scrollbar(right, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side="right", fill="y")

        # Buttons below the table
        btn_frame = tk.Frame(right, bg="#ffffff")
        btn_frame.pack(fill="x", pady=(8, 0))

        ttk.Button(btn_frame, text="📋 Copy Password", command=self.copy_password).pack(side="left", expand=True, fill="x", padx=(0, 3))
        ttk.Button(btn_frame, text="🗑️ Delete", command=self.delete_password).pack(side="left", expand=True, fill="x", padx=(3, 0))

        # Load all passwords into the table
        self.load_passwords()

        # Keyboard shortcut: Ctrl+S to save
        self.root.bind("<Control-s>", lambda event: self.save_password())

    # ============================================================
    # EVENT HANDLERS (Dashboard Actions)
    # ============================================================

    def fill_generated_password(self):
        """Generates a random password and fills it into the password field."""
        self.entry_password.delete(0, tk.END)
        self.entry_password.insert(0, generate_random_password())

    def save_password(self):
        """Saves a new password entry to the database."""
        website = self.entry_website.get().strip()
        username = self.entry_username.get().strip()
        password = self.entry_password.get().strip()

        # Validation
        if not website or not username or not password:
            messagebox.showwarning("Missing Fields", "Please fill in all fields.")
            return

        # Encode the password before storing
        encoded = encode_password(password)

        conn = sqlite3.connect(get_db_path())
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO passwords (website, username, password) VALUES (?, ?, ?)",
            (website, username, encoded)
        )
        conn.commit()
        conn.close()

        messagebox.showinfo("Saved", f"Password for '{website}' saved successfully!")

        # Clear the input fields
        self.entry_website.delete(0, tk.END)
        self.entry_username.delete(0, tk.END)
        self.entry_password.delete(0, tk.END)

        # Refresh the table
        self.load_passwords()

    def load_passwords(self):
        """Loads all saved passwords from the database into the table."""
        # Clear the current table
        for row in self.tree.get_children():
            self.tree.delete(row)

        conn = sqlite3.connect(get_db_path())
        cursor = conn.cursor()
        cursor.execute("SELECT id, website, username, password FROM passwords")
        rows = cursor.fetchall()
        conn.close()

        for row in rows:
            record_id, website, username, encoded_pass = row
            decoded = decode_password(encoded_pass)
            # Show password as masked in the table
            masked = "*" * len(decoded)
            self.tree.insert("", "end", iid=record_id, values=(website, username, masked))

    def search_passwords(self):
        """Searches passwords by website name (filters the table)."""
        query = self.search_var.get().strip().lower()

        # Clear the current table
        for row in self.tree.get_children():
            self.tree.delete(row)

        conn = sqlite3.connect(get_db_path())
        cursor = conn.cursor()
        cursor.execute(
            "SELECT id, website, username, password FROM passwords WHERE LOWER(website) LIKE ?",
            (f"%{query}%",)
        )
        rows = cursor.fetchall()
        conn.close()

        for row in rows:
            record_id, website, username, encoded_pass = row
            decoded = decode_password(encoded_pass)
            masked = "*" * len(decoded)
            self.tree.insert("", "end", iid=record_id, values=(website, username, masked))

    def copy_password(self):
        """Copies the selected password to the clipboard."""
        selected = self.tree.selection()
        if not selected:
            messagebox.showinfo("No Selection", "Please select a password entry first.")
            return

        record_id = selected[0]

        conn = sqlite3.connect(get_db_path())
        cursor = conn.cursor()
        cursor.execute("SELECT password FROM passwords WHERE id=?", (record_id,))
        result = cursor.fetchone()
        conn.close()

        if result:
            decoded = decode_password(result[0])
            self.root.clipboard_clear()
            self.root.clipboard_append(decoded)
            messagebox.showinfo("Copied", "Password copied to clipboard!")

    def delete_password(self):
        """Deletes the selected password entry from the database."""
        selected = self.tree.selection()
        if not selected:
            messagebox.showinfo("No Selection", "Please select a password entry to delete.")
            return

        # Confirmation dialog
        confirm = messagebox.askyesno("Confirm Delete", "Are you sure you want to delete this entry?")
        if not confirm:
            return

        record_id = selected[0]

        conn = sqlite3.connect(get_db_path())
        cursor = conn.cursor()
        cursor.execute("DELETE FROM passwords WHERE id=?", (record_id,))
        conn.commit()
        conn.close()

        messagebox.showinfo("Deleted", "Password entry deleted.")
        self.load_passwords()

# ============================================================
# RUN THE APPLICATION
# ============================================================

if __name__ == "__main__":
    root = tk.Tk()
    app = PasswordManagerApp(root)
    root.mainloop()
