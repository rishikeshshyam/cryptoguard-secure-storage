import os
import glob
import random
import json
import base64
import tkinter as tk
from tkinter import filedialog, messagebox

def load_photos(folder_path):
    images = glob.glob(os.path.join(folder_path, '*.jpg'))
    return images

def upload_and_split_data(file_path, chunk_size=1024):
    with open(file_path, 'rb') as f:
        data = f.read()
    chunks = [data[i:i+chunk_size] for i in range(0, len(data), chunk_size)]
    return chunks

def assign_chunks_to_photos(chunks, photos):
    if len(chunks) > len(photos):
        raise ValueError("Not enough photos to store all chunks.")
    selected_photos = random.sample(photos, len(chunks))
    assignments = dict(zip(selected_photos, chunks))
    return assignments

def save_mapping(assignments, mapping_file="mapping.json"):
    encoded_assignments = {photo: base64.b64encode(chunk).decode('utf-8') for photo, chunk in assignments.items()}
    with open(mapping_file, 'w') as f:
        json.dump(encoded_assignments, f)

def load_mapping(mapping_file="mapping.json"):
    with open(mapping_file, 'r') as f:
        encoded_assignments = json.load(f)
    assignments = {photo: base64.b64decode(chunk) for photo, chunk in encoded_assignments.items()}
    return assignments

def reassemble_data(assignments):
    data = b''
    for photo, chunk in assignments.items():
        data += chunk
    return data

class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Photo Storage System")
        self.geometry("400x400")
        self.configure(bg="#2e2e2e")
        self.folder_path = ""
        self.file_path = ""
        self.assignments = {}

        self.title_label = tk.Label(self, text="CRYPTOGUARD", font=("Segoe UI", 20, "bold"), bg="#2e2e2e", fg="#00cfff")
        self.title_label.pack(pady=20)

        self.folder_label = tk.Label(self, text="Select Photos Folder:", bg="#2e2e2e", fg="white", font=("Segoe UI", 12))
        self.folder_label.pack(pady=10)

        self.folder_button = tk.Button(self, text="Browse 📁", command=self.browse_folder, bg="#007acc", fg="white", font=("Segoe UI", 12), borderwidth=0)
        self.folder_button.pack(pady=5)

        self.file_label = tk.Label(self, text="Upload a File:", bg="#2e2e2e", fg="white", font=("Segoe UI", 12))
        self.file_label.pack(pady=10)

        self.upload_button = tk.Button(self, text="Upload 📤", command=self.upload_file, bg="#007acc", fg="white", font=("Segoe UI", 12), borderwidth=0)
        self.upload_button.pack(pady=5)

        self.save_button = tk.Button(self, text="Save Mapping 💾", command=self.save_mapping, bg="#007acc", fg="white", font=("Segoe UI", 12), borderwidth=0)
        self.save_button.pack(pady=10)

        self.retrieve_button = tk.Button(self, text="Retrieve Data 📥", command=self.retrieve_data, bg="#007acc", fg="white", font=("Segoe UI", 12), borderwidth=0)
        self.retrieve_button.pack(pady=5)

    def browse_folder(self):
        self.folder_path = filedialog.askdirectory()
        if self.folder_path:
            photos = load_photos(self.folder_path)
            messagebox.showinfo("Folder Selected", f"Loaded {len(photos)} photos.")
        else:
            messagebox.showwarning("Folder Not Selected", "Please select a valid folder.")

    def upload_file(self):
        self.file_path = filedialog.askopenfilename()
        if self.file_path and self.folder_path:
            photos = load_photos(self.folder_path)
            chunks = upload_and_split_data(self.file_path)

            if len(photos) < len(chunks):
                messagebox.showerror("Error", "Not enough photos to store all chunks.")
                return
            
            self.assignments = assign_chunks_to_photos(chunks, photos)
            messagebox.showinfo("File Uploaded", f"Data assigned to {len(self.assignments)} photos.")
        else:
            messagebox.showwarning("Error", "Please select a folder and upload a file.")

    def save_mapping(self):
        if self.assignments:
            save_mapping(self.assignments)
            messagebox.showinfo("Success", "Mapping saved successfully.")
        else:
            messagebox.showwarning("Error", "No mapping available to save.")

    def retrieve_data(self):
        if os.path.exists("mapping.json"):
            assignments = load_mapping()
            retrieved_data = reassemble_data(assignments)

            with open("reassembled_file", 'wb') as f:
                f.write(retrieved_data)

            messagebox.showinfo("Success", "Data successfully retrieved and reassembled.")
        else:
            messagebox.showerror("Error", "No saved mapping found.")

if __name__ == "__main__":
    app = App()
    app.mainloop()
