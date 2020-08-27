import tkinter as tk

class PPLineNumbers(tk.Canvas):
    def __init__(self, master, text_widget,  **kwargs):
        super().__init__(master, **kwargs)
        self.text_widget = text_widget



    def redraw(self, *args):
        '''redraw line numbers'''
        self.delete("all")
        print("redraw")

        i = self.text_widget.index("@0,0")
        while True:
            dline = self.text_widget.dlineinfo(i)
            print(dline)
            if dline is None:
                break
            y = dline[1]
            linenum = str(i).split(".")[0]
            self.create_text(2, y, anchor="nw", text=linenum)
            i = self.text_widget.index("%s+1line" % i)


