import customtkinter as ctk
import subprocess
from datetime import datetime
import os
from tkinter import filedialog, messagebox
import json
from PIL import Image
import shutil

# Set appearance
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

APP_DATA_FILE = "launcher_apps.json"
ICONS_FOLDER = "app_icons"

# Ensure icons folder exists
if not os.path.exists(ICONS_FOLDER):
    os.makedirs(ICONS_FOLDER)

# Main app setup
app = ctk.CTk()
app.geometry("800x600")
app.title("Game Launcher")
app.iconbitmap("gamepad.ico") if os.path.exists("gamepad.ico") else None

# Create a frame for the top section (time and title)
top_frame = ctk.CTkFrame(app, corner_radius=10, fg_color="#212121")
top_frame.pack(fill="x", padx=20, pady=10)

# App title
title_label = ctk.CTkLabel(top_frame, text="ต้องการเปิดอะไร", font=("Kanit", 24, "bold"))
title_label.pack(pady=5)

# Time label
time_label = ctk.CTkLabel(top_frame, text="", font=("Kanit", 14))
time_label.pack(pady=5)

def update_time():
    time_label.configure(text=datetime.now().strftime("%H:%M:%S"))
    app.after(1000, update_time)

update_time()

# Create a scrollable frame for app buttons
apps_frame = ctk.CTkScrollableFrame(app, corner_radius=10)
apps_frame.pack(fill="both", expand=True, padx=20, pady=10)

# Create a frame for control buttons
control_frame = ctk.CTkFrame(app, corner_radius=10, fg_color="#212121")
control_frame.pack(fill="x", padx=20, pady=10)

# Dictionaries and lists to keep track of apps
added_app_buttons = []
added_app_paths = {}
app_frames = {}  # To store frames for each app

def open_game(game_path):
    try:
        subprocess.Popen(game_path, shell=True)
    except Exception as e:
        messagebox.showerror("Error", f"ไม่สามารถเปิดแอปพลิเคชันได้: {e}")

def save_apps():
    app_data = []
    for button_text, app_info in added_app_paths.items():
        app_data.append({
            "name": button_text.replace("เปิด ", ""),
            "path": app_info["path"],
            "icon_path": app_info["icon_path"]
        })
    with open(APP_DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(app_data, f, ensure_ascii=False)

def remove_app(app_name, app_frame):
    # Remove the UI frame
    app_frame.destroy()
    
    # Remove from our lists and dictionaries
    button_text = f"เปิด {app_name}"
    if button_text in added_app_paths:
        del added_app_paths[button_text]
    
    if app_name in app_frames:
        del app_frames[app_name]
    
    # Save changes
    save_apps()
    messagebox.showinfo("Success", f"ลบแอปพลิเคชัน '{app_name}' เรียบร้อยแล้ว")

def create_app_button(app_name, file_path, icon_path=None):
    # Create a frame for this app with rounded corners
    app_frame = ctk.CTkFrame(apps_frame, corner_radius=8)
    app_frame.pack(fill="x", padx=10, pady=5)
    app_frames[app_name] = app_frame
    
    # Horizontal layout inside the frame
    button_text = f"เปิด {app_name}"
    
    # App icon (if available)
    if icon_path and os.path.exists(icon_path):
        try:
            img = ctk.CTkImage(dark_image=Image.open(icon_path), size=(32, 32))
            icon_label = ctk.CTkLabel(app_frame, image=img, text="")
            icon_label.pack(side="left", padx=10, pady=5)
        except Exception:
            pass
    
    # Create button
    new_btn = ctk.CTkButton(
        app_frame, 
        text=button_text, 
        command=lambda path=file_path: open_game(path),
        height=40,
        width=200,
        font=("Kanit", 12),
        fg_color="#3498db",  # Blue color
        hover_color="#2980b9"
    )
    new_btn.pack(side="left", padx=10, pady=5, fill="x", expand=True)
    
    # Create delete button
    del_btn = ctk.CTkButton(
        app_frame,
        text="ลบ",
        command=lambda name=app_name, frame=app_frame: remove_app(name, frame),
        fg_color="#E53935",
        hover_color="#C62828",
        width=60,
        height=40,
        font=("Kanit", 12)
    )
    del_btn.pack(side="right", padx=10, pady=5)
    
    added_app_buttons.append(new_btn)
    added_app_paths[button_text] = {"path": file_path, "icon_path": icon_path}
    
    return app_frame

def load_apps():
    if os.path.exists(APP_DATA_FILE):
        with open(APP_DATA_FILE, "r", encoding="utf-8") as f:
            try:
                app_data = json.load(f)
                for app_info in app_data:
                    app_name = app_info["name"]
                    file_path = app_info["path"]
                    icon_path = app_info.get("icon_path", None)
                    create_app_button(app_name, file_path, icon_path)
            except json.JSONDecodeError:
                messagebox.showerror("Error", "ไฟล์ข้อมูลแอปพลิเคชันเสียหาย")

def copy_icon(source_path, app_name):
    """Copy the icon to our icons folder and return the new path"""
    if not source_path:
        return None
        
    # Extract extension
    _, ext = os.path.splitext(source_path)
    
    # Create a unique filename 
    destination = os.path.join(ICONS_FOLDER, f"{app_name}{ext}")
    
    try:
        shutil.copy2(source_path, destination)
        return destination
    except Exception:
        return None

def add_app():
    # Get file path - allow ALL file types
    file_path = filedialog.askopenfilename(
        title="เลือกไฟล์แอปพลิเคชันหรือเกม",
        filetypes=[
            ("All Files", "*.*"),
            ("Programs", "*.exe"),
            ("Shortcuts", "*.lnk")
        ]
    )
    if not file_path:
        return
        
    # Get app name from file path or let user customize
    base_name = os.path.basename(file_path)
    app_name = os.path.splitext(base_name)[0]  # Remove extension
    
    # Ask for icon (optional)
    icon_path = filedialog.askopenfilename(
        title="เลือกไอคอนสำหรับแอปพลิเคชัน (ไม่บังคับ)",
        filetypes=[
            ("Image files", "*.png *.jpg *.jpeg *.ico *.bmp"),
            ("All Files", "*.*")
        ]
    )
    
    if icon_path:
        # Copy the icon to our folder
        local_icon_path = copy_icon(icon_path, app_name)
    else:
        local_icon_path = None
    
    # Add to UI
    create_app_button(app_name, file_path, local_icon_path)
    
    # Save to file
    save_apps()
# Add apps from saved file
load_apps()

# Add control buttons with improved styling
add_icon = Image.open("add_icon.png") if os.path.exists("add_icon.png") else None
if add_icon:
    add_img = ctk.CTkImage(dark_image=add_icon, size=(24, 24))
else:
    add_img = None

add_btn = ctk.CTkButton(
    control_frame, 
    text="เพิ่มแอป",
    image=add_img,
    compound="left",
    command=add_app,
    font=("Kanit", 14),
    height=45,
    fg_color="#4CAF50",
    hover_color="#388E3C"
)
add_btn.pack(side="left", padx=20, pady=10, expand=True, fill="x")

exit_icon = Image.open("exit_icon.png") if os.path.exists("exit_icon.png") else None
if exit_icon:
    exit_img = ctk.CTkImage(dark_image=exit_icon, size=(24, 24))
else:
    exit_img = None

exit_btn = ctk.CTkButton(
    control_frame, 
    text="ออก",
    image=exit_img,
    compound="left",
    command=app.quit,
    font=("Kanit", 14),
    height=45,
    fg_color="#F44336",
    hover_color="#D32F2F"
)
exit_btn.pack(side="right", padx=20, pady=10, expand=True, fill="x")

# Start the app
app.mainloop()
