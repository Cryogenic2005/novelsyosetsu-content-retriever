import asyncio
import csv
import os
import tkinter as tk
from threading import Thread

from translate_handler import translate_chapters

class ViewChapterUI(tk.Frame):
    def __init__(self, master, app, novel: str, chapter: int, **kwargs):
        super().__init__(master)
        self.app = app
        self.novel = novel
        self.chapter = chapter
        self.storage_path = kwargs.get('storage_path', None)
        self.api_key = kwargs.get('api_key', os.getenv('GEMINI_API_KEY', ''))
        
        self.chapter_content = self.load_chapter_content()
        self.translated = self.chapter_content is not None
        self.is_translating = False
        if self.chapter_content is None:
            self.chapter_content = "This chapter has not been translated yet. Please request a translation."
        
        self.create_widgets()
        self.add_key_bindings()

    def load_chapter_content(self) -> str | None:
        # Placeholder: Load chapter content from a file or database
        chapter_file_path = os.path.join(self.storage_path,
                                         self.novel,
                                         "translation",
                                         f"chapter_{self.chapter}_translated.txt")
        
        content_txt = None
        if not os.path.exists(chapter_file_path):
            content_txt = None
        else:
            with open(chapter_file_path, 'r', encoding='utf-8') as file:
                content_txt = file.read().strip()
        
        # Split the content into title and body
        if content_txt:
            title_txt = content_txt.split('\n')[0] if content_txt else "No Title"
            story_txt = content_txt[len(title_txt):].strip() if title_txt else content_txt
            
            content_txt = f"{title_txt}\n\n{story_txt}"
        
        return content_txt

    def create_widgets(self):
        # Create frame for chapter header
        header_frame = tk.Frame(self)
        header_frame.pack(fill=tk.X, padx=10, pady=5)
        header_label = tk.Label(header_frame, text=f"{self.novel} - Chapter {self.chapter}",
                                font=("Arial", 16, "bold"),
                                bg="#0000ff", fg="#333")
        header_label.pack(fill=tk.X, padx=10, pady=5)
        header_label.config(bg="#0000ff", fg="#ffffff")  # Set background and foreground colors
        
        if not self.translated:
            tk.Button(self, text="Translate", command=self.request_translation).pack(padx=5)
        
        # Create a text widget to display the chapter content
        text_frame = tk.Frame(self)
        text_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Create vertical scrollbar
        scrollbar = tk.Scrollbar(text_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Create text widget with scrollbar
        self.text_widget = tk.Text(text_frame,
                                   wrap=tk.WORD,
                                   font=("Arial", 12),
                                   padx=10, pady=10,
                                   bg="#ffffff", fg="#333",
                                   yscrollcommand=scrollbar.set)
        self.text_widget.insert(tk.END, self.chapter_content)
        self.text_widget.config(state=tk.DISABLED)  # Make the text widget read-only
        self.text_widget.pack(fill=tk.BOTH, expand=True)
        
        # Configure scrollbar to work with the text widget
        scrollbar.config(command=self.text_widget.yview)
        
        # Add a title tag for the chapter title
        self.text_widget.tag_configure("title", font=("Arial", 12, "bold"), foreground="#000000")
        self.text_widget.tag_add("title", "1.0", "1.end")
        
        # Create frame for navigation buttons
        nav_frame = tk.Frame(self)
        nav_frame.pack(pady=5)
        tk.Button(nav_frame, text="Previous", command=self.go_previous).pack(side=tk.LEFT, padx=5)
        tk.Button(nav_frame, text="Back", command=self.go_back).pack(side=tk.LEFT, padx=5)
        tk.Button(nav_frame, text="Next", command=self.go_next).pack(side=tk.LEFT, padx=5)
        
    def add_key_bindings(self):
        # Bind keys for navigation to the frame
        self.master.bind("<Left>", lambda e: self.go_previous())
        self.master.bind("<Right>", lambda e: self.go_next())
        self.master.bind("<Escape>", lambda e: self.go_back())
        
        # Bind keys for scrolling to the frame
        self.master.bind("<Up>", lambda e: self.text_widget.yview_scroll(-1, "units"))
        self.master.bind("<Down>", lambda e: self.text_widget.yview_scroll(1, "units"))
        
        # Hotkey for translation request
        if not self.translated:
            self.master.bind("<Return>", lambda e: self.request_translation())
        
    def request_translation(self):
        if self.is_translating:
            tk.messagebox.showinfo("Info", "Translation is already in progress. Please wait.")
            return
        
        if not self.api_key:
            tk.messagebox.showerror("Error", "API key is required for translation.")
            return
                
        novel_catalog_path = os.path.join(self.storage_path, "novels.csv")

        # Read the novel catalog to find the link for the selected novel
        link = None
        with open(novel_catalog_path, 'r', newline='') as file:
            reader = csv.reader(file)
            next(reader)
            
            for row in reader:
                if row[0].strip() == self.novel:
                    link = row[1].strip().strip('\"')
                    break
            else:
                tk.messagebox.showerror("Error", f"Novel '{self.novel}' not found in the catalog.")
                return
        
        # Run the async translation in a background thread to avoid blocking the UI
        def run_async_translation():
            asyncio.run(translate_chapters(
                novel_link=link,
                novel_name=self.novel,
                chapter_idxs=[ self.chapter ],
                api_key=self.api_key,
                storage_path=self.storage_path
            ))
            self.after(0, self.on_translation_complete)
            
        Thread(target=run_async_translation, daemon=True).start()
        tk.messagebox.showinfo("Info", "Translation started. This may take a while. You will be notified when it finishes.")
    
    def on_translation_complete(self):
        tk.messagebox.showinfo("Info", "Translation completed successfully.")
        
        self.app.show_frame(
            __import__('ui.view_chapter', fromlist=['ViewChapterUI']).ViewChapterUI,
            novel=self.novel,
            chapter=self.chapter,
            storage_path=self.storage_path
        )

    def go_previous(self):
        prev_chapter = self.chapter - 1
        # Placeholder: check if next chapter is translated, if not, translate it
        if prev_chapter > 0:
            self.app.show_frame(
                __import__('ui.view_chapter', fromlist=['ViewChapterUI']).ViewChapterUI,
                novel=self.novel,
                chapter=prev_chapter,
                storage_path=self.storage_path
            )

    def go_next(self):
        next_chapter = self.chapter + 1
        self.app.show_frame(
            __import__('ui.view_chapter', fromlist=['ViewChapterUI']).ViewChapterUI,
            novel=self.novel,
            chapter=next_chapter,
            storage_path=self.storage_path
        )
        
    def go_back(self):
        self.app.show_frame(
            __import__('ui.select_chapters', fromlist=['SelectChaptersUI']).SelectChaptersUI,
            novel=self.novel,
            storage_path=self.storage_path
        )
        
    def destroy(self):
        # Unbind all key bindings to prevent memory leaks
        self.master.unbind("<Left>")
        self.master.unbind("<Right>")
        self.master.unbind("<Escape>")
        self.master.unbind("<Up>")
        self.master.unbind("<Down>")
        self.master.unbind("<Return>")
        
        super().destroy()