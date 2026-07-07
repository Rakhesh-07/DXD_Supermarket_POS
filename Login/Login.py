import customtkinter as ctk
import db_adapter
import time
from PIL import Image

# Global variables required by main.py
v = 0
emp_name = ""
emp_role = ""
emp_username = ""

# Set customtkinter styling
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

# Create main window
win = ctk.CTk()
win.title("DXD Supermarket - Login")

# Query exact display information from OS
import ctypes
try:
    w = ctypes.windll.user32.GetSystemMetrics(0)
    h = ctypes.windll.user32.GetSystemMetrics(1)
except Exception:
    w = win.winfo_screenwidth()
    h = win.winfo_screenheight()

win.geometry(f"{w}x{h}+0+0")

import sys

def close_app():
    try:
        win.quit()
        win.destroy()
    except Exception:
        pass
    sys.exit(0)

win.protocol("WM_DELETE_WINDOW", close_app)

# Load and scale background image (stretched to cover)
try:
    bg_image = ctk.CTkImage(
        light_image=Image.open("Login/logo/bg1.jpg"),
        dark_image=Image.open("Login/logo/bg1.jpg"),
        size=(w, h)
    )
    bg_label = ctk.CTkLabel(win, image=bg_image, text="")
    bg_label.place(x=0, y=0, relwidth=1, relheight=1)
    
    # Handle dynamic screen resize (DPI scaling / Fullscreen changes)
    def on_resize(event):
        if event.widget == win:
            bg_image.configure(size=(event.width, event.height))
    win.bind("<Configure>", on_resize)
except Exception as e:
    print(f"Error loading background: {e}")
    win.configure(fg_color="#1e1e1e")

# Central Login Card
card_frame = ctk.CTkFrame(win, width=400, height=450, corner_radius=15, fg_color=("#ffffff", "#2b2b2b"), border_width=2, border_color="#eaab06")
card_frame.place(relx=0.5, rely=0.5, anchor="center")

# DXD Logo in the Card
try:
    logo_image = ctk.CTkImage(
        light_image=Image.open("logo.png"),
        dark_image=Image.open("logo.png"),
        size=(150, 150)
    )
    logo_label = ctk.CTkLabel(card_frame, image=logo_image, text="")
    logo_label.place(relx=0.5, rely=0.2, anchor="center")
except Exception:
    # Fallback text logo
    logo_label = ctk.CTkLabel(card_frame, text="DXD Supermarket", font=("Arial", 24, "bold"), text_color="#eaab06")
    logo_label.place(relx=0.5, rely=0.15, anchor="center")

# Title
title_lbl = ctk.CTkLabel(card_frame, text="Staff Login", font=("Arial", 18, "bold"))
title_lbl.place(relx=0.5, rely=0.38, anchor="center")

# Username entry
user_entry = ctk.CTkEntry(card_frame, width=280, placeholder_text="Username", height=40, font=("Arial", 14))
user_entry.place(relx=0.5, rely=0.50, anchor="center")

# Password entry
pass_entry = ctk.CTkEntry(card_frame, width=280, placeholder_text="Password", show="*", height=40, font=("Arial", 14))
pass_entry.place(relx=0.5, rely=0.62, anchor="center")

# Feedback label
feedback_lbl = ctk.CTkLabel(card_frame, text="", font=("Arial", 13, "bold"), text_color="red")
feedback_lbl.place(relx=0.5, rely=0.72, anchor="center")

def toggle_password():
    if pass_entry.cget("show") == "*":
        pass_entry.configure(show="")
        show_btn.configure(text="Hide")
    else:
        pass_entry.configure(show="*")
        show_btn.configure(text="Show")

show_btn = ctk.CTkButton(card_frame, text="Show", width=50, height=20, fg_color="transparent", text_color="#eaab06", hover_color="#3a3a3a", font=("Arial", 11), command=toggle_password)
show_btn.place(relx=0.8, rely=0.62, anchor="center")

def handle_login():
    global v, emp_name, emp_role, emp_username
    username = user_entry.get().strip()
    password = pass_entry.get().strip()
    
    if not username or not password:
        feedback_lbl.configure(text="All fields are required!", text_color="red")
        return
        
    try:
        pass_hash = db_adapter.hash_password(password)
        result = db_adapter.execute_query(
            "SELECT name, role FROM EMPLOYEES WHERE username = ? AND password_hash = ?",
            (username, pass_hash),
            fetch="one"
        )
        
        if result:
            emp_name, emp_role = result
            emp_username = username
            feedback_lbl.configure(text="Login Successful!", text_color="green")
            win.update()
            
            v = 1
            win.quit()
            win.destroy()
        else:
            feedback_lbl.configure(text="Invalid Username or Password!", text_color="red")
            pass_entry.delete(0, 'end')
            
    except Exception as e:
        feedback_lbl.configure(text=f"Database connection error!", text_color="red")
        print(f"Login error: {e}")

# OK and Close Buttons
login_btn = ctk.CTkButton(card_frame, text="Login", width=130, height=35, fg_color="#eaab06", text_color="black", hover_color="#c89205", font=("Arial", 14, "bold"), command=handle_login)
login_btn.place(relx=0.35, rely=0.84, anchor="center")

close_btn = ctk.CTkButton(card_frame, text="Close", width=130, height=35, fg_color="#cfcfcf", text_color="black", hover_color="#b5b5b5", font=("Arial", 14, "bold"), command=close_app)
close_btn.place(relx=0.65, rely=0.84, anchor="center")

# Enter binding
win.bind("<Return>", lambda e: handle_login())
win.bind("<Escape>", lambda e: close_app())

win.mainloop()
