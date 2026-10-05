import os
import shutil
import time
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

# Temporary or junk extensions to target for cleanup
junk_extensions = [".tmp", ".log", ".bak", ".old"]

def organize_files():
    target_dir = filedialog.askdirectory(title="Select Folder to Organize")
    if not target_dir:
        return
    
    log_box.delete("1.0", tk.END)
    log_box.insert(tk.END, f"Starting organization in:\n{target_dir}\n" + "-"*48 + "\n")
    root.update()
    
    try:
        os.chdir(target_dir)
        moved_count = 0
        category_counts = {cat: 0 for cat in folders}
        
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
                    
                    log_box.insert(tk.END, f"Moved: {filename} -> {category}/\n")
                    log_box.see(tk.END)
                    root.update()
                    
                    moved_count += 1
                    category_counts[category] += 1
                    break
                    
        log_box.insert(tk.END, "-"*48 + f"\nDone! Successfully organized {moved_count} files.\n\nSummary:\n")
        for cat, count in category_counts.items():
            if count > 0:
                log_box.insert(tk.END, f"  - {cat}: {count}\n")
        log_box.see(tk.END)
                
        messagebox.showinfo("Success!", f"Organized {moved_count} files successfully!")
    except Exception as e:
        messagebox.showerror("Error", f"An error occurred: {e}")

def clean_old_files():
    target_dir = filedialog.askdirectory(title="Select Folder to Clean Up")
    if not target_dir:
        return
        
    # Confirm safety choice with the user first
    confirm = messagebox.askyesno(
        "Safe Cleanup", 
        "This will scan for temporary junk files and files older than 90 days, and safely move them into a '_Trash_Bin' folder.\n\nDo you want to proceed?"
    )
    if not confirm:
        return

    log_box.delete("1.0", tk.END)
    log_box.insert(tk.END, f"Starting safe cleanup in:\n{target_dir}\n" + "-"*48 + "\n")
    root.update()
    
    try:
        os.chdir(target_dir)
        trash_dir = "_Trash_Bin"
        cleaned_count = 0
        now = time.time()
        ninety_days_in_seconds = 90 * 86400  # 90 days
        
        for filename in os.listdir():
            if os.path.isdir(filename) or filename == "main.py":
                continue
                
            file_path = filename
            _, file_ext = os.path.splitext(filename)
            file_ext = file_ext.lower()
            
            # Check if it's junk or older than 90 days
            is_junk = file_ext in junk_extensions
            file_age = now - os.path.getmtime(file_path)
            is_old = file_age > ninety_days_in_seconds
            
            if is_junk or is_old:
                if not os.path.exists(trash_dir):
                    os.mkdir(trash_dir)
                    
                shutil.move(file_path, os.path.join(trash_dir, filename))
                
                reason = "Junk file" if is_junk else "Inactive > 90 days"
                log_box.insert(tk.END, f"Quarantined: {filename} ({reason})\n")
                log_box.see(tk.END)
                root.update()
                cleaned_count += 1
                
        log_box.insert(tk.END, "-"*48 + f"\nCleanup complete! Moved {cleaned_count} items to '{trash_dir}'.\n")
        messagebox.showinfo("Cleanup Complete", f"Safely moved {cleaned_count} items to the '_Trash_Bin' folder.")
    except Exception as e:
        messagebox.showerror("Error", f"An error occurred: {e}")

# Build the Pro desktop app window
root = tk.Tk()
root.title("File Organizer Pro")
root.geometry("500x530")
root.configure(bg="#f7f7f7")

# Header
title_label = tk.Label(root, text="File Organizer Pro", font=("Arial", 16, "bold"), bg="#f7f7f7", fg="#333")
title_label.pack(pady=12)

# Action Buttons Frame
button_frame = tk.Frame(root, bg="#f7f7f7")
button_frame.pack(pady=5)

select_button = tk.Button(button_frame, text="Select Folder & Organize", font=("Arial", 10, "bold"), bg="#2563eb", fg="white", padx=10, pady=8, bd=0, cursor="hand2", command=organize_files)
select_button.pack(side=tk.LEFT, padx=5)

clean_button = tk.Button(button_frame, text="Clean Junk / Old Files", font=("Arial", 10, "bold"), bg="#dc2626", fg="white", padx=10, pady=8, bd=0, cursor="hand2", command=clean_old_files)
clean_button.pack(side=tk.LEFT, padx=5)

# Live Activity Log Box (Terminal style)
log_box = scrolledtext.ScrolledText(root, width=56, height=17, font=("Consolas", 9), bg="#1e1e1e", fg="#00ff00")
log_box.pack(pady=15)

# Start application loop
root.mainloop()