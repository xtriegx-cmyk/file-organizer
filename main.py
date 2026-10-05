import json
import logging
import os
import shutil
import sys
import time
import tkinter as tk
from tkinter import filedialog, messagebox, scrolledtext
import winshell
from win32com.client import Dispatch

# Setup Professional Logging
logging.basicConfig(
    filename="app.log",
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s"
)

# Load External Configuration
CONFIG_FILE = "config.json"
default_config = {
    "categories": {
        "Images": [".jpg", ".png"],
        "Documents": [".pdf", ".docx"]
    },
    "junk_extensions": [".tmp", ".log"],
    "trash_days_threshold": 90
}

def load_config():
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, "r") as f:
                return json.load(f)
        except Exception as e:
            logging.error(f"Failed to load config: {e}")
    return default_config

config = load_config()
folders = config.get("categories", {})
junk_extensions = config.get("junk_extensions", [])
trash_threshold = config.get("trash_days_threshold", 90) * 86400

# Track histories for undo functions
organize_history = []
cleanup_history = []
current_target_dir = ""

def create_desktop_shortcut():
    """Automatically creates a desktop shortcut on first run if it doesn't exist."""
    try:
        desktop = winshell.desktop()
        shortcut_path = os.path.join(desktop, "File Organizer Pro.lnk")
        
        if not os.path.exists(shortcut_path):
            target = sys.executable
            shell = Dispatch('WScript.Shell')
            shortcut = shell.CreateShortcut(shortcut_path)
            shortcut.TargetPath = target
            shortcut.WorkingDirectory = os.path.dirname(target)
            shortcut.IconLocation = target
            shortcut.Save()
            logging.info("Desktop shortcut created successfully.")
    except Exception as e:
        logging.error(f"Could not create desktop shortcut: {e}")

def show_about():
    messagebox.showinfo("About File Organizer Pro", "File Organizer Pro v1.3\nEnterprise-grade local file management utility.")

def show_help():
    messagebox.showinfo("Quick Help", "• Organize Files: Sorts files into categories defined in config.json.\n• Clean Junk Files: Quarantines temporary files securely.\n• Undo Buttons: Revert recent organization or cleanup runs.")

def organize_files():
    global current_target_dir, organize_history
    target_dir = filedialog.askdirectory(title="Select Folder to Organize")
    if not target_dir:
        return
    
    current_target_dir = target_dir
    organize_history.clear()
    
    log_box.delete("1.0", tk.END)
    log_box.insert(tk.END, f"Starting organization in:\n{target_dir}\n" + "-"*52 + "\n")
    status_bar.config(text="Status: Organizing files...")
    root.update()
    
    try:
        os.chdir(target_dir)
        moved_count = 0
        
        for filename in os.listdir():
            if os.path.isdir(filename) or filename in ["main.py", "config.json", "app.log"]:
                continue
                
            _, file_ext = os.path.splitext(filename)
            file_ext = file_ext.lower()
            
            for category, extensions in folders.items():
                if file_ext in extensions:
                    if not os.path.exists(category):
                        os.mkdir(category)
                    
                    src_path = filename
                    dest_path = os.path.join(category, filename)
                    
                    shutil.move(src_path, dest_path)
                    organize_history.append((filename, category))
                    
                    log_box.insert(tk.END, f"Moved: {filename} -> {category}/\n")
                    log_box.see(tk.END)
                    root.update()
                    
                    moved_count += 1
                    logging.info(f"Organized: {filename} into {category}")
                    break
                    
        log_box.insert(tk.END, "-"*52 + f"\nDone! Successfully organized {moved_count} files.\n")
        status_bar.config(text=f"Status: Idle - Organized {moved_count} files")
        logging.info(f"Organization complete. Moved {moved_count} files in {target_dir}")
        messagebox.showinfo("Success!", f"Organized {moved_count} files successfully!")
    except Exception as e:
        status_bar.config(text="Status: Error encountered")
        logging.error(f"Error during organization: {e}")
        messagebox.showerror("Error", f"An error occurred: {e}")

def clean_junk_files():
    global current_target_dir, cleanup_history
    target_dir = filedialog.askdirectory(title="Select Folder to Clean Junk Files")
    if not target_dir:
        return
    
    current_target_dir = target_dir
    cleanup_history.clear()
    
    log_box.delete("1.0", tk.END)
    log_box.insert(tk.END, f"Starting junk cleanup in:\n{target_dir}\n" + "-"*52 + "\n")
    status_bar.config(text="Status: Cleaning junk files...")
    root.update()
    
    try:
        os.chdir(target_dir)
        junk_folder = "Quarantine_Junk"
        cleaned_count = 0
        
        for filename in os.listdir():
            if os.path.isdir(filename) or filename in ["main.py", "config.json", "app.log"]:
                continue
                
            _, file_ext = os.path.splitext(filename)
            file_ext = file_ext.lower()
            
            if file_ext in junk_extensions:
                if not os.path.exists(junk_folder):
                    os.mkdir(junk_folder)
                
                src_path = filename
                dest_path = os.path.join(junk_folder, filename)
                
                shutil.move(src_path, dest_path)
                cleanup_history.append((filename, junk_folder))
                
                log_box.insert(tk.END, f"Quarantined: {filename} -> {junk_folder}/\n")
                log_box.see(tk.END)
                root.update()
                
                cleaned_count += 1
                logging.info(f"Quarantined junk file: {filename}")
                
        log_box.insert(tk.END, "-"*52 + f"\nCleanup done! Quarantined {cleaned_count} files.\n")
        status_bar.config(text=f"Status: Idle - Cleaned {cleaned_count} files")
        logging.info(f"Cleanup complete. Quarantined {cleaned_count} files in {target_dir}")
        messagebox.showinfo("Success!", f"Cleaned and quarantined {cleaned_count} files successfully!")
    except Exception as e:
        status_bar.config(text="Status: Error during cleanup")
        logging.error(f"Error during cleanup: {e}")
        messagebox.showerror("Error", f"An error occurred during cleanup: {e}")

def undo_organize():
    global organize_history, current_target_dir
    if not organize_history or not current_target_dir:
        messagebox.showinfo("Undo Organize", "No recent organize history to undo in this session.")
        return
    
    if not messagebox.askyesno("Confirm Undo", "Move recently organized files back to the main directory?"):
        return

    log_box.delete("1.0", tk.END)
    log_box.insert(tk.END, "Starting Undo Organize...\n" + "-"*52 + "\n")
    status_bar.config(text="Status: Undoing organization...")
    root.update()

    try:
        os.chdir(current_target_dir)
        restored_count = 0

        for filename, category in organize_history:
            category_path = os.path.join(category, filename)
            if os.path.exists(category_path):
                shutil.move(category_path, filename)
                log_box.insert(tk.END, f"Restored: {filename} <- {category}/\n")
                log_box.see(tk.END)
                root.update()
                restored_count += 1
                logging.info(f"Undid organize: {filename} from {category}")
                
                if os.path.exists(category) and not os.listdir(category):
                    os.rmdir(category)

        organize_history.clear()
        log_box.insert(tk.END, "-"*52 + f"\nUndo complete! Restored {restored_count} files.\n")
        status_bar.config(text=f"Status: Idle - Restored {restored_count} files")
        messagebox.showinfo("Success", f"Successfully restored {restored_count} files!")
    except Exception as e:
        status_bar.config(text="Status: Error during undo")
        logging.error(f"Error during undo organize: {e}")
        messagebox.showerror("Error", f"An error occurred: {e}")

def undo_cleanup():
    global cleanup_history, current_target_dir
    if not cleanup_history or not current_target_dir:
        messagebox.showinfo("Undo Cleanup", "No recent cleanup history to undo in this session.")
        return
    
    if not messagebox.askyesno("Confirm Undo", "Move quarantined junk files back to the main directory?"):
        return

    log_box.delete("1.0", tk.END)
    log_box.insert(tk.END, "Starting Undo Cleanup...\n" + "-"*52 + "\n")
    status_bar.config(text="Status: Undoing cleanup...")
    root.update()

    try:
        os.chdir(current_target_dir)
        restored_count = 0
        junk_folder = "Quarantine_Junk"

        for filename, _ in cleanup_history:
            junk_path = os.path.join(junk_folder, filename)
            if os.path.exists(junk_path):
                shutil.move(junk_path, filename)
                log_box.insert(tk.END, f"Restored: {filename} <- {junk_folder}/\n")
                log_box.see(tk.END)
                root.update()
                restored_count += 1
                logging.info(f"Undid cleanup: {filename}")
                
                if os.path.exists(junk_folder) and not os.listdir(junk_folder):
                    os.rmdir(junk_folder)

        cleanup_history.clear()
        log_box.insert(tk.END, "-"*52 + f"\nUndo complete! Restored {restored_count} files.\n")
        status_bar.config(text=f"Status: Idle - Restored {restored_count} files")
        messagebox.showinfo("Success", f"Successfully restored {restored_count} files!")
    except Exception as e:
        status_bar.config(text="Status: Error during undo cleanup")
        logging.error(f"Error during undo cleanup: {e}")
        messagebox.showerror("Error", f"An error occurred: {e}")

# Build window UI
root = tk.Tk()
root.title("File Organizer Pro")
root.geometry("540x690")
root.configure(bg="#0f172a")

status_bar = tk.Label(root, text="Status: Ready", font=("Segoe UI", 8), bg="#090d16", fg="#94a3b8", anchor=tk.W, padx=10, pady=5)
status_bar.pack(side=tk.BOTTOM, fill=tk.X)

menubar = tk.Menu(root)
file_menu = tk.Menu(menubar, tearoff=0)
file_menu.add_command(label="Exit", command=root.quit)
menubar.add_cascade(label="File", menu=file_menu)
help_menu = tk.Menu(menubar, tearoff=0)
help_menu.add_command(label="Quick Help", command=show_help)
help_menu.add_command(label="About", command=show_about)
menubar.add_cascade(label="Help", menu=help_menu)
root.config(menu=menubar)

header_frame = tk.Frame(root, bg="#1e293b", pady=12)
header_frame.pack(fill=tk.X, padx=12, pady=(10, 8))
tk.Label(header_frame, text="File Organizer Pro", font=("Segoe UI", 16, "bold"), bg="#1e293b", fg="#f8fafc").pack()
tk.Label(header_frame, text="Intelligent File Management & Safe Quarantine", font=("Segoe UI", 9), bg="#1e293b", fg="#94a3b8").pack(pady=(2, 0))

control_frame = tk.Frame(root, bg="#0f172a")
control_frame.pack(pady=4)

button_frame_1 = tk.Frame(control_frame, bg="#0f172a")
button_frame_1.pack(pady=5)
tk.Button(button_frame_1, text="Organize Files", font=("Segoe UI", 9, "bold"), bg="#2563eb", fg="white", width=19, pady=8, bd=0, cursor="hand2", command=organize_files).pack(side=tk.LEFT, padx=6)
tk.Button(button_frame_1, text="Clean Junk Files", font=("Segoe UI", 9, "bold"), bg="#dc2626", fg="white", width=19, pady=8, bd=0, cursor="hand2", command=clean_junk_files).pack(side=tk.LEFT, padx=6)

# Second row of buttons: Undo Organize and Undo Cleanup side-by-side
button_frame_2 = tk.Frame(control_frame, bg="#0f172a")
button_frame_2.pack(pady=2)
tk.Button(button_frame_2, text="Undo Organize", font=("Segoe UI", 9, "bold"), bg="#334155", fg="white", width=19, pady=6, bd=0, cursor="hand2", command=undo_organize).pack(side=tk.LEFT, padx=6)
tk.Button(button_frame_2, text="Undo Cleanup", font=("Segoe UI", 9, "bold"), bg="#334155", fg="white", width=19, pady=6, bd=0, cursor="hand2", command=undo_cleanup).pack(side=tk.LEFT, padx=6)

log_container = tk.Frame(root, bg="#1e293b", padx=8, pady=8)
log_container.pack(padx=12, pady=8, fill=tk.BOTH, expand=True)
log_box = scrolledtext.ScrolledText(log_container, width=60, height=12, font=("Consolas", 9), bg="#090d16", fg="#22c55e", bd=0, highlightthickness=0)
log_box.pack(fill=tk.BOTH, expand=True)

# Run shortcut creation on startup
create_desktop_shortcut()

root.mainloop()