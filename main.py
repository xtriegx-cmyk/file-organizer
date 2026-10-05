import os
import shutil

# Define categories and their file extensions
folders = {
    "Images": [".jpg", ".jpeg", ".png", ".gif"],
    "Documents": [".pdf", ".docx", ".txt", ".xlsx"],
    "Code": [".py", ".js", ".html", ".css"],
    "Archives": [".zip", ".rar", ".7z"]
}

# Get the folder path from the user
target_dir = input("Enter the path of the folder to organize: ").strip('"\'')

if os.path.exists(target_dir):
    os.chdir(target_dir)
    
    # Loop through every file in the directory
    for filename in os.listdir():
        # Skip folders and this script itself
        if os.path.isdir(filename) or filename == "main.py":
            continue
            
        # Get the file extension
        _, file_ext = os.path.splitext(filename)
        file_ext = file_ext.lower()
        
        # Check which category the extension belongs to
        for category, extensions in folders.items():
            if file_ext in extensions:
                # Create the category folder if it doesn't exist yet
                if not os.path.exists(category):
                    os.mkdir(category)
                    
                # Move the file into the folder
                shutil.move(filename, os.path.join(category, filename))
                print(f"Moved: {filename} -> {category}/")
                break
                
    print("\nFile organization complete!")
else:
    print("Error: That folder path does not exist.")