import os
import shutil
import tkinter as tk
from tkinter import filedialog, messagebox, scrolledtext

# Expanded categories and file extensions
folders = {
    "Images": [".jpg", ".jpeg", ".png", ".gif", ".webp"],
    "Documents": [".pdf", ".docx", ".txt", ".xlsx", ".doc", ".pptx"],
    "Code": [".py", ".js", ".html", ".css", ".cpp", ".json"],
    "Archives": [".zip", ".rar", ".7z", ".tar", ".gz"],
    "Audio": [".mp3", ".wav", ".flac", ".aac"],
    "Videos": [".mp4", ".mkv", ".mov", ".avi"],
    "Data": [".csv", ".sql", ".db"]
}

def organize_files():
    target_dir = filedialog.askdirectory(title="Select Folder to Organize")
    if not target_dir:
        return
    
    # Clear log and show start message
    log_box.delete("1.0", tk.END)
    log_box.insert(tk.END, f"Starting organization in:\n{target_dir}\n" + "-"*48 + "\n")
    root.update()
    
    try:
        os.chdir(target_dir)
        moved_count = 0
        
        for filename in os.listdir():
            if os.path.isdir(filename) or filename == "main.py":
                continue
                
            _, file_ext = os.path.splitext(filename)
            file_ext = file_ext.lower()
            
            for category, extensions in folders.items():
                if file_ext in extensions:
                    if not os.path.exists(category):
                        os.mkdir(category)
                    shutil.move(filename, os.path.join(category, filename))
                    
                    # Print live update to the app's log window
                    log_box.insert(tk.END, f"Moved: {filename} -> {category}/\n")
                    log_box.see(tk.END)
                    root.update()
                    
                    moved_count += 1
                    break
                    
        log_box.insert(tk.END, "-"*48 + f"\nDone! Successfully organized {moved_count} files.\n")
        messagebox.showinfo("Success!", f"Organized {moved_count} files successfully!")
    except Exception as e:
        messagebox.showerror("Error", f"An error occurred: {e}")

# Build the Pro desktop app window
root = tk.Tk()
root.title("File Organizer Pro")
root.geometry("500x440")
root.configure(bg="#f7f7f7")

# Header
title_label = tk.Label(root, text="File Organizer Pro", font=("Arial", 16, "bold"), bg="#f7f7f7", fg="#333")
title_label.pack(pady=15)

# Action Button
select_button = tk.Button(root, text="Select Folder & Organize", font=("Arial", 11, "bold"), bg="#2563eb", fg="white", padx=15, pady=8, bd=0, cursor="hand2", command=organize_files)
select_button.pack(pady=5)

# Live Activity Log Box (Terminal style)
log_box = scrolledtext.ScrolledText(root, width=56, height=15, font=("Consolas", 9), bg="#1e1e1e", fg="#00ff00")
log_box.pack(pady=15)

# Start application loop
root.mainloop()