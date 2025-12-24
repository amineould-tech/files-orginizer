import os, shutil, threading
import tkinter as tk
from tkinter import filedialog, ttk

class UniversalOrganizer:
    def __init__(self, root):
        self.root = root
        self.root.title("Quick File Organizer")
        self.root.geometry("450x450")
        
        # --- THEME COLORS ---
        self.dark_mode = True
        self.colors = {
            "dark":  {"bg": "#2b2b2b", "fg": "#ffffff", "btn": "#3c3f41", "accent": "#27ae60"},
            "light": {"bg": "#f0f0f0", "fg": "#000000", "btn": "#e1e1e1", "accent": "#2ecc71"}
        }

        # --- DATA CONFIG ---
        self.categories = {
            "IMAGES": [".jpg", ".jpeg", ".png", ".gif", ".bmp", ".webp"],
            "DOCUMENTS": [".pdf", ".docx", ".doc", ".txt", ".xlsx", ".csv"],
            "VIDEOS": [".mp4", ".mkv", ".mov", ".avi"],
            "MUSIC": [".mp3", ".wav", ".flac"],
            "ARCHIVES": [".zip", ".rar", ".7z", ".tar"],
            "INSTALLERS": [".exe", ".msi"]
        }
        self.ignore_folders = ["bin", "obj", "node_modules", ".git", "AppData"]
        self.scan_path = ""
        self.dest_path = ""

        # --- UI ELEMENTS ---
        self.main_frame = tk.Frame(self.root)
        self.main_frame.pack(fill="both", expand=True)

        self.title_label = tk.Label(self.main_frame, text="Universal File Organizer", font=("Arial", 18, "bold"))
        self.title_label.pack(pady=15)
        
        # Theme Toggle Button
        self.theme_btn = tk.Button(self.main_frame, text="🌙 Switch Theme", command=self.toggle_theme, font=("Arial", 8))
        self.theme_btn.pack(pady=5)

        self.btn_s = tk.Button(self.main_frame, text="📁 1. Select Folder to Clean", command=self.set_scan, width=25)
        self.btn_s.pack(pady=10)
        
        self.btn_d = tk.Button(self.main_frame, text="🎯 2. Select Destination", command=self.set_dest, width=25)
        self.btn_d.pack(pady=10)
        
        self.progress = ttk.Progressbar(self.main_frame, length=300, mode='determinate')
        self.progress.pack(pady=20)
        
        self.start_btn = tk.Button(self.main_frame, text="START ORGANIZING", font=("Arial", 10, "bold"), 
                                   command=self.start_thread, width=20)
        self.start_btn.pack(pady=5)
        
        self.status = tk.Label(self.main_frame, text="Ready", font=("Arial", 9))
        self.status.pack(pady=10)

        self.apply_theme() # Apply default theme

    def toggle_theme(self):
        self.dark_mode = not self.dark_mode
        self.apply_theme()

    def apply_theme(self):
        theme = self.colors["dark"] if self.dark_mode else self.colors["light"]
        
        self.root.configure(bg=theme["bg"])
        self.main_frame.configure(bg=theme["bg"])
        self.title_label.configure(bg=theme["bg"], fg=theme["fg"])
        self.status.configure(bg=theme["bg"], fg=theme["fg"])
        self.theme_btn.configure(bg=theme["btn"], fg=theme["fg"])
        self.btn_s.configure(bg=theme["btn"], fg=theme["fg"])
        self.btn_d.configure(bg=theme["btn"], fg=theme["fg"])
        self.start_btn.configure(bg=theme["accent"], fg="white")

    def set_scan(self): 
        self.scan_path = filedialog.askdirectory()
        if self.scan_path: self.status.config(text=f"Scan: {os.path.basename(self.scan_path)}")

    def set_dest(self): 
        self.dest_path = filedialog.askdirectory()
        if self.dest_path: self.status.config(text=f"Save to: {os.path.basename(self.dest_path)}")

    def start_thread(self):
        if not self.scan_path or not self.dest_path: return
        threading.Thread(target=self.logic, daemon=True).start()

    def logic(self):
        self.start_btn.config(state="disabled")
        files_to_move = []
        
        for root, dirs, files in os.walk(self.scan_path):
            dirs[:] = [d for d in dirs if d not in self.ignore_folders]
            if os.path.abspath(root).startswith(os.path.abspath(self.dest_path)): continue
            for f in files:
                files_to_move.append(os.path.join(root, f))

        total = len(files_to_move)
        if total == 0:
            self.status.config(text="No files found!")
            self.start_btn.config(state="normal")
            return

        for i, path in enumerate(files_to_move):
            filename = os.path.basename(path)
            ext = os.path.splitext(filename)[1].lower()
            
            target_folder_name = "OTHERS"
            for category, extensions in self.categories.items():
                if ext in extensions:
                    target_folder_name = category
                    break
            
            if not ext: continue

            target_dir = os.path.join(self.dest_path, target_folder_name)
            os.makedirs(target_dir, exist_ok=True)
            
            try:
                shutil.copy2(path, os.path.join(target_dir, filename))
            except:
                pass
            
            self.progress['value'] = ((i+1)/total)*100
            self.status.config(text=f"Sorting: {filename[:25]}...")
            self.root.update_idletasks()

        self.status.config(text="Finished! Folder is clean.")
        self.start_btn.config(state="normal")

if __name__ == "__main__":
    root = tk.Tk()
    app = UniversalOrganizer(root)
    root.mainloop()
    