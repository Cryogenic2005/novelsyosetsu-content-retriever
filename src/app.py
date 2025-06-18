import tkinter as tk

from ui import SelectNovelsUI

class App:
    def __init__(self, **kwargs):
        self.root = tk.Tk()
        self.root.title("Novel Translator")
        self.root.configure(bg="#f0f0f0")
        self.root.resizable(True, True)
        self.root.geometry("800x600")
        self.root.minsize(800, 600)
        
        if kwargs.get("fullscreen", False):
            self.root.attributes("-fullscreen", True)
            
        self.root.bind("<F11>", lambda e: self.root.attributes("-fullscreen",
                                                               not self.root.attributes("-fullscreen")))
        
        self.current_frame: tk.Frame = None
        self.show_frame(SelectNovelsUI, **kwargs)

    def show_frame(self, frame_class: type[tk.Frame], **kwargs):
        if self.current_frame is not None:
            self.current_frame.destroy()
        self.current_frame = frame_class(self.root, self, **kwargs)
        self.current_frame.pack(fill="both", expand=True)

    def run(self):
        self.root.mainloop()