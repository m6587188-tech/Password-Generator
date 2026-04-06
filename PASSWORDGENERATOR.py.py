import random
import string
import time
from tkinter import messagebox

# --- ML Libraries ---
from sklearn.linear_model import LogisticRegression
import numpy as np

# --- GUI Libraries ---
import ttkbootstrap as ttk
from ttkbootstrap.constants import *


# --- GLOBAL VARIABLES ---
app_password = None
lock_time = 0
attempts_left = 3
last_fail_time = 0
selected_password_var = None
ml_model = None

# --- GUI Widgets for the selected password ---
selected_password_entry = None


# --- ML: FEATURE EXTRACTION ---
def extract_features(password):
    length = len(password)
    digits = sum(c.isdigit() for c in password)
    upper = sum(c.isupper() for c in password)
    lower = sum(c.islower() for c in password)
    symbols = sum(c in string.punctuation for c in password)
    return [length, digits, upper, lower, symbols]

# --- ML: TRAIN MODEL ---
def train_ml_model():
    global ml_model
    data = [
        ("abc", "Weak"), ("abcd123", "Weak"), ("Pass@123", "Medium"),
        ("Password1", "Medium"), ("StrongP@ss12!", "Strong"),
        ("QwErTy@2024", "Strong"), ("123456", "Weak"), ("HelloW", "Weak"),
        ("Stronger!2024", "Strong"), ("Mypassword", "Medium"),
    ]
    X = [extract_features(pwd) for pwd, lbl in data]
    y = [lbl for _, lbl in data]
    ml_model = LogisticRegression(max_iter=1000)
    ml_model.fit(X, y)

# --- ML: PREDICT STRENGTH ---
def predict_strength(password):
    features = np.array([extract_features(password)])
    return ml_model.predict(features)[0]


# --- CORE FUNCTIONS ---
def update_selected_password_display(password):
    selected_password_entry.configure(state="normal")
    selected_password_entry.delete(0, END)
    selected_password_entry.insert(0, password)
    selected_password_entry.configure(state="readonly")
    
def generate_passwords():
    try:
        length = int(length_entry.get())
    except ValueError:
        messagebox.showerror("Error", "Enter a valid number!")
        return

    characters = ""
    if letters_choice.get(): characters += string.ascii_letters
    if digits_choice.get(): characters += string.digits
    if symbols_choice.get(): characters += string.punctuation
    if not characters:
        messagebox.showwarning("Error", "Select at least one option!")
        return

    for widget in passwords_frame.winfo_children():
        widget.destroy()

    global selected_password_var
    selected_password_var = ttk.StringVar()
    for i in range(3):
        password = "".join(random.choice(characters) for _ in range(length))
        strength = predict_strength(password)
        rb = ttk.Radiobutton(
            passwords_frame,
            text=f"Option {i+1}: {password}   ({strength})",
            variable=selected_password_var,
            value=password,
            bootstyle="info",
            command=lambda p=password: update_selected_password_display(p)
        )
        rb.pack(fill="x", pady=2)

def copy_password():
    password_to_copy = selected_password_entry.get()
    if password_to_copy:
        root.clipboard_clear()
        root.clipboard_append(password_to_copy)
        messagebox.showinfo("Copied!", "Password copied to clipboard.")
    else:
        messagebox.showwarning("Empty", "No password to copy.")


def set_selected_password():
    global app_password
    if not selected_password_var or not selected_password_var.get():
        messagebox.showwarning("Error", "Select a password first!")
        return
    app_password = selected_password_var.get()
    messagebox.showinfo("Password Set", "Password has been set successfully!")
    show_login_page()


def login_attempt():
    global attempts_left, lock_time, last_fail_time

    if time.time() < last_fail_time + lock_time:
        wait_time = int(last_fail_time + lock_time - time.time())
        messagebox.showwarning("Locked", f"Too many attempts! Try again in {wait_time} seconds.")
        return

    entered_password = login_entry.get()

    if entered_password == app_password:
        messagebox.showinfo("Success", "Access Granted! ✅")
        attempts_left = 3
        lock_time = 0
    else:
        attempts_left -= 1
        if attempts_left > 0:
            messagebox.showerror("Error", f"Wrong password! {attempts_left} attempts left.")
        else:
            if lock_time == 0: lock_time = 30
            else: lock_time *= 2
            last_fail_time = time.time()
            attempts_left = 3
            messagebox.showwarning("Locked", f"Too many attempts! Locked for {lock_time} seconds.")


def show_login_page():
    generator_frame.pack_forget()
    login_frame.pack(pady=20)


# --- GUI SETUP ---
root = ttk.Window(themename="litera") # THEME CHANGE HERE
root.title("Secure Password Generator (ML)")
root.geometry("550x600")

# --- INITIAL SETUP ---
train_ml_model()

# --- PASSWORD GENERATOR PAGE (Frame 1) ---
generator_frame = ttk.Frame(root, padding=10)
generator_frame.pack(pady=20, padx=20, fill="both", expand=True)

ttk.Label(generator_frame, text="Password Generator", font=("Arial", 16, "bold")).pack(pady=10)
ttk.Label(generator_frame, text="Enter Password Length:").pack()
length_entry = ttk.Entry(generator_frame)
length_entry.pack(pady=5)

letters_choice = ttk.BooleanVar(value=True)
digits_choice = ttk.BooleanVar(value=True)
symbols_choice = ttk.BooleanVar(value=True)

ttk.Checkbutton(generator_frame, text="Include Letters", variable=letters_choice, bootstyle="round-toggle").pack(pady=2)
ttk.Checkbutton(generator_frame, text="Include Digits", variable=digits_choice, bootstyle="round-toggle").pack(pady=2)
ttk.Checkbutton(generator_frame, text="Include Symbols", variable=symbols_choice, bootstyle="round-toggle").pack(pady=2)

ttk.Button(generator_frame, text="Generate Passwords", command=generate_passwords, bootstyle="success").pack(pady=15)

passwords_frame = ttk.Frame(generator_frame)
passwords_frame.pack(pady=10, fill="x")

# --- Password Display and Copy Section ---
password_display_frame = ttk.Frame(generator_frame)
password_display_frame.pack(pady=10, fill="x")

ttk.Label(password_display_frame, text="Selected Password:", font=("Arial", 10)).pack(side="left", padx=(0, 5))
selected_password_entry = ttk.Entry(password_display_frame, bootstyle="success", state="readonly")
selected_password_entry.pack(side="left", expand=True, fill="x")

ttk.Button(password_display_frame, text="Copy", command=copy_password, bootstyle="info").pack(side="left", padx=5)

ttk.Button(generator_frame, text="Set Selected as App Lock", command=set_selected_password, bootstyle="primary").pack(pady=10)

# --- LOGIN PAGE (Frame 2, initially hidden) ---
login_frame = ttk.Frame(root, padding=10)

ttk.Label(login_frame, text="App Lock Login", font=("Arial", 16, "bold")).pack(pady=10)
ttk.Label(login_frame, text="Enter your app password:").pack()
login_entry = ttk.Entry(login_frame, show="*")
login_entry.pack(pady=5)

ttk.Button(login_frame, text="Login", command=login_attempt, bootstyle="success").pack(pady=10)

# --- RUN THE APP ---
root.mainloop()
