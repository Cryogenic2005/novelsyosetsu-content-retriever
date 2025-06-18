import os
import csv
import tkinter as tk

class SelectNovelsUI(tk.Frame):
    def __init__(self, master, app, **kwargs):
        super().__init__(master)
        self.app = app
        
        if 'storage_path' not in kwargs:
            raise ValueError("Storage path must be provided in kwargs.")
        
        self.storage_path = kwargs['storage_path']
        self.novels = self.get_novels()

        self.create_widgets()

    def get_novels(self):
        novel_catalog_filepath = os.path.join(self.storage_path, 'novels.csv')
        
        with open(novel_catalog_filepath, 'r', newline='') as file:
            reader = csv.reader(file)
            next(reader)
            
            novels = []
            for row in reader:
                if len(row) >= 2:
                    novel_name = row[0].strip()
                    link = row[1].strip()
                    if novel_name and link:
                        novels.append(novel_name)
    
        return novels    

    def create_widgets(self):
        tk.Label(self, text="Select a Novel", font=("Arial", 18)).pack(pady=20)
        self.listbox = tk.Listbox(self)
        for novel in self.novels:
            self.listbox.insert(tk.END, novel)
        self.listbox.pack(pady=10)
        tk.Button(self, text="View Selected Novel", command=self.select_novel).pack(pady=5)
        tk.Button(self, text="Add New Novel", command=self.add_new_novel).pack(pady=5)

    def select_novel(self):
        selection = self.listbox.curselection()
        if selection:
            novel = self.listbox.get(selection[0])
            self.app.show_frame(
                __import__('ui.select_chapters', fromlist=['SelectChaptersUI']).SelectChaptersUI,
                novel=novel,
                storage_path=self.storage_path
            )

    def add_new_novel(self):
        self.app.show_frame(
            __import__('ui.new_novel', fromlist=['NewNovelUI']).NewNovelUI,
            storage_path=self.storage_path
        )
