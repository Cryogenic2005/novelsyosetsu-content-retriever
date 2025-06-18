import csv
import os
import tkinter as tk

class NewNovelUI(tk.Frame):
    def __init__(self, master, app, **kwargs):
        super().__init__(master)
        self.app = app
        if 'storage_path' not in kwargs:
            raise ValueError("Storage path must be provided in kwargs.")
        
        self.storage_path = kwargs['storage_path']
        
        self.create_widgets()

    def create_widgets(self):
        tk.Label(self, text="Add New Novel", font=("Arial", 18)).pack(pady=20)
        
        tk.Label(self, text="Novel Link:").pack()
        self.link_entry = tk.Entry(self, width=50)
        self.link_entry.pack(pady=5)
        
        tk.Label(self, text="Novel Name:").pack()
        self.name_entry = tk.Entry(self, width=50)
        self.name_entry.pack(pady=5)
        
        tk.Button(self, text="Add Novel", command=self.add_novel).pack(pady=10)
        tk.Button(self, text="Back", command=self.go_back).pack(pady=5)

    def add_novel(self):
        link = self.link_entry.get().strip()
        name = self.name_entry.get().strip()
        
        if link and name:
            novel_catalog_filepath = os.path.join(self.storage_path, 'novels.csv')
            with open(novel_catalog_filepath, 'a', newline='') as file:
                writer = csv.writer(file)
                writer.writerow([name, link])
            
            tk.messagebox.showinfo("Success", f"Novel '{name}' added successfully!")
            
            self.app.show_frame(
                __import__('ui.select_novels', fromlist=['SelectNovelsUI']).SelectNovelsUI,
                storage_path=self.storage_path
            )
        else:
            tk.messagebox.showerror("Error", "Both fields must be filled out.")

    def go_back(self):
        self.app.show_frame(
            __import__('ui.select_novels', fromlist=['SelectNovelsUI']).SelectNovelsUI,
            storage_path=self.storage_path
        )
