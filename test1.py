import tkinter as tk

from enhancedtext import Enhanced_Text

class TestText(Enhanced_Text):
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)

        self.master = master

        self.bind("<<TextChanged>>", self.changes_occured)

    def changes_occured(self, event=None):
        print(f"Changes in range {self.last_change_range}")
        print(self.convert_index_to_canonical(self.last_change_range[0]))

if __name__ == '__main__':
    c = tk.Tk()
    t = TestText(c)
    t.pack(side=tk.TOP, fill=tk.BOTH, expand=1)
    c.mainloop()

