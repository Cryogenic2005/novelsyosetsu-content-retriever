import os
import tkinter as tk

class ViewChapterUI(tk.Frame):
    def __init__(self, master, app, novel, chapter, **kwargs):
        super().__init__(master)
        self.app = app
        self.novel = novel
        self.chapter = chapter
        self.storage_path = kwargs.get('storage_path', None)
        
        self.chapter_content = self.load_chapter_content()
        self.create_widgets()

    def load_chapter_content(self):
        header_txt = f"{self.novel} Chapter {self.chapter}"
        
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
        if not content_txt:
            return f"{header_txt}\n\nNo content available."
        
        title_txt = content_txt.split('\n')[0] if content_txt else "No Title"
        content_txt = content_txt[len(title_txt):].strip() if title_txt else content_txt
        
        return f"{header_txt}\n{title_txt}\n\n{content_txt}"

    def create_widgets(self):
        text_frame = tk.Frame(self)
        text_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        self.text_widget = tk.Text(text_frame,
                                   wrap=tk.WORD,
                                   font=("Arial", 12),
                                   padx=10, pady=10,
                                   bg="#ffffff", fg="#333")
        self.text_widget.insert(tk.END, self.chapter_content)
        self.text_widget.config(state=tk.DISABLED)  # Make the text widget read-only
        self.text_widget.pack(fill=tk.BOTH, expand=True)
        
        # Add a header tag for the chapter title
        self.text_widget.tag_configure("header", font=("Arial", 14, "bold"), foreground="#0000ff")
        self.text_widget.tag_add("header", "1.0", "1.end")
        
        # Add a title tag for the chapter title
        self.text_widget.tag_configure("title", font=("Arial", 12, "bold"), foreground="#000000")
        self.text_widget.tag_add("title", "2.0", "2.end")
        
        nav_frame = tk.Frame(self)
        nav_frame.pack(pady=5)
        tk.Button(nav_frame, text="Previous", command=self.go_previous).pack(side=tk.LEFT, padx=5)
        tk.Button(nav_frame, text="Next", command=self.go_next).pack(side=tk.LEFT, padx=5)
        tk.Button(self, text="Back", command=self.go_back).pack(pady=10)

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
        # Placeholder: check if next chapter is translated, if not, translate it
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
