import os
import shutil
import threading
import customtkinter as ctk
from tkinter import filedialog

# Set the appearance mode
ctk.set_appearance_mode("System")
ctk.set_default_color_theme("blue")

class FileOrganizerApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        # --- 1. WINDOW SETUP ---
        self.title("AI File Classifier & Organizer")
        self.geometry("600x450")
        
        # --- 2. CONFIGURATION ---
        self.ignore_list = [".ini", ".tmp", ".sys", ".lnk", ".log", ".bak"]
        self.archive_types = [".zip", ".rar", ".7z", ".tar", ".gz", ".iso"]
        self.scan_path = ""
        self.dest_path = ""

        # --- 3. UI ELEMENTS ---
        self.label = ctk.CTkLabel(self, text="Smart File Organizer", font=("Arial", 26, "bold"))
        self.label.pack(pady=(30, 10))

        self.sub_label = ctk.CTkLabel(self, text="Organize any file type into neat folders", font=("Arial", 12))
        self.sub_label.pack(pady=(0, 20))

        # Button: Folder to Scan
        self.btn_scan = ctk.CTkButton(self, text="1. Select Folder to Scan", command=self.select_scan, height=40)
        self.btn_scan.pack(pady=10)

        # Button: Destination Folder
        self.btn_dest = ctk.CTkButton(self, text="2. Select Where to Save", command=self.select_dest, height=40)
        self.btn_dest.pack(pady=10)

        # Progress Bar
        self.progress = ctk.CTkProgressBar(self, width=450)
        self.progress.set(0)
        self.progress.pack(pady=25)

        # Start Button
        self.btn_start = ctk.CTkButton(self, text="Start Classification", fg_color="#2ecc71", hover_color="#27ae60", 
                                      command=self.run_thread, height=50, font=("Arial", 16, "bold"))
        self.btn_start.pack(pady=10)

        # Status Label
        self.status = ctk.CTkLabel(self, text="Status: Ready", font=("Arial", 11))
        self.status.pack(pady=10)

    # --- 4. LOGIC FUNCTIONS ---

    def select_scan(self):
        path = filedialog.askdirectory()
        if path:
            self.scan_path = path
            self.status.configure(text=f"Ready to scan: {os.path.basename(path)}")

    def select_dest(self):
        path = filedialog.askdirectory()
        if path:
            self.dest_path = path
            self.status.configure(text=f"Ready to save in: {os.path.basename(path)}")

    def run_thread(self):
        if not self.scan_path or not self.dest_path:
            self.status.configure(text="Error: Please select both folders first!", text_color="red")
            return
        # Start the organization in a separate thread so the UI doesn't freeze
        threading.Thread(target=self.organize_logic, daemon=True).start()

    def organize_logic(self):
        self.btn_start.configure(state="disabled")
        self.status.configure(text_color="white")

        # Step A: Gather and count files
        all_files = []
        for root, dirs, files in os.walk(self.scan_path):
            # Safety: Don't scan the destination if it's inside the scan folder
            if os.path.abspath(root).startswith(os.path.abspath(self.dest_path)):
                continue
            for f in files:
                all_files.append(os.path.join(root, f))
        
        total_files = len(all_files)
        if total_files == 0:
            self.status.configure(text="Status: No files found to organize.")
            self.btn_start.configure(state="normal")
            return

        # Step B: Process files
        for i, file_path in enumerate(all_files):
            filename = os.path.basename(file_path)
            name, extension = os.path.splitext(filename)
            ext_lower = extension.lower()

            # 1. Check Ignore List
            if ext_lower in self.ignore_list or not extension:
                continue

            # 2. Determine Folder Name (Handle archives as one group)
            if ext_lower in self.archive_types:
                folder_name = "COMPRESSED_ARCHIVES"
            else:
                folder_name = ext_lower.replace(".", "").upper()

            # 3. Create Target Folder
            target_folder = os.path.join(self.dest_path, folder_name)
            os.makedirs(target_folder, exist_ok=True)

            # 4. Copy File
            try:
                shutil.copy2(file_path, os.path.join(target_folder, filename))
            except Exception as e:
                print(f"Error copying {filename}: {e}")

            # 5. Update UI
            progress_value = (i + 1) / total_files
            self.progress.set(progress_value)
            self.status.configure(text=f"Organizing: {filename[:30]}...")

        self.status.configure(text="Status: SUCCESS! All files organized.", text_color="#2ecc71")
        self.btn_start.configure(state="normal")

if __name__ == "__main__":
    app = FileOrganizerApp()
    app.mainloop()