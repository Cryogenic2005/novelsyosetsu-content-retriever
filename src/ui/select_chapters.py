import csv
import os
import re
import tkinter as tk

from translate_handler import translate_chapters

class SelectChaptersUI(tk.Frame):
    def __init__(self, master, app, novel, **kwargs):
        super().__init__(master)
        self.app = app
        self.novel = novel
        self.novel_link = ""
        
        if 'storage_path' not in kwargs:
            raise ValueError("Storage path must be provided in kwargs.")
        
        self.storage_path = kwargs['storage_path']
        self.api_key = kwargs.get('api_key', None)
        
        self.chapters = self.get_chapters()
        self.create_widgets()

    def get_chapters(self) -> list[int]:
        # Locate novel catalog
        novel_catalog_filepath = os.path.join(self.storage_path, 'novels.csv')
        if not os.path.exists(novel_catalog_filepath):
            raise FileNotFoundError(f"Novel catalog not found at {novel_catalog_filepath}.")
        
        # Read the novel catalog to find the link for the selected novel
        with open(novel_catalog_filepath, 'r', newline='') as file:
            reader = csv.reader(file)
            next(reader)
            
            for row in reader:
                if row[0].strip() == self.novel:
                    self.novel_link = row[1].strip()
                    break
            else:
                raise ValueError(f"Novel '{self.novel}' not found in the catalog.")
        
        # Locate directory for the novel translations
        novel_dir = os.path.join(self.storage_path, self.novel)
        translation_dir = os.path.join(novel_dir, 'translation')
        
        # Create the directory if it doesn't exist
        os.makedirs(novel_dir, exist_ok=True)
        os.makedirs(translation_dir, exist_ok=True)
        
        # Read chapter files and determine their chapter numbers
        # Chapter files are expected to be named like "Chapter_1_translated.txt"
        chapters: list[int] = []
        
        for filename in os.listdir(translation_dir):
            match = re.match(r'Chapter_(\d+)_translated\.txt', filename)
            if match:
                chapter_number = int(match.group(1))
                chapters.append(chapter_number)
                
        # Sort chapters in ascending order
        chapters.sort()
        return chapters
                
    def create_widgets(self):
        tk.Label(self, text=f"Novel: {self.novel}", font=("Arial", 16)).pack(pady=10)
        
        tk.Label(self, text="Chapters:").pack()
        self.listbox = tk.Listbox(self)
        for idx in self.chapters:
            label = f"Chapter {idx}"
            self.listbox.insert(tk.END, label)
        self.listbox.pack(pady=5)
        tk.Button(self, text="View Chapter", command=self.view_chapter).pack(pady=5)
        
        tk.Label(self, text="Enter chapter numbers to translate (space separated):").pack()
        self.chapter_entry = tk.Entry(self, width=30)
        self.chapter_entry.pack(pady=2)
        tk.Button(self, text="Translate Chapters", command=self.translate_chapters).pack(pady=5)
        
        tk.Button(self, text="Back", command=self.go_back).pack(pady=10)

    def view_chapter(self):
        selection = self.listbox.curselection()
        if selection:
            idx = self.chapters[selection[0]]
            self.app.show_frame(
                __import__('ui.view_chapter', fromlist=['ViewChapterUI']).ViewChapterUI,
                novel=self.novel,
                chapter=idx,
                storage_path=self.storage_path
            )

    def translate_chapters(self):
        chapter_input = self.chapter_entry.get().strip()
        if not chapter_input:
            tk.messagebox.showerror("Error", "Please enter chapter numbers to translate.")
            return
        
        try:
            chapter_idxs = list(map(int, chapter_input.split()))
        except ValueError:
            tk.messagebox.showerror("Error", "Invalid chapter numbers. Please enter integers separated by spaces.")
            return
        
        if not self.api_key:
            tk.messagebox.showerror("Error", "API key is required for translation.")
            return
        
        result = translate_chapters(
            novel_link=self.novel_link,
            novel_name=self.novel,
            chapter_idxs=chapter_idxs,
            api_key=self.api_key,
            storage_path=self.storage_path
        )
        
        if result:
            tk.messagebox.showinfo("Translation Result", result)
        else:
            tk.messagebox.showinfo("Translation Result", "Chapters translated successfully!")

    def go_back(self):
        self.app.show_frame(
            __import__('ui.select_novels', fromlist=['SelectNovelsUI']).SelectNovelsUI,
            storage_path=self.storage_path
        )
