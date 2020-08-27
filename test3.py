import tkinter as tk

class TestText(tk.Text):
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)

        self.master = master
        self.c = tk.Canvas(self)
        self.c.create_line(0,10,200,10)

        #bindings
        self.bind('<Key>', self.key_pressed)
        self.bind('<Control-p>', self.show_canvas)
        self.bind('<<Modified>>', self.mod)

        self.mark_set("sentinel", tk.INSERT)
        self.mark_gravity("sentinel", tk.LEFT)

    def show_canvas(self, event=None):

        self.window_create("2.0", window=self.c)
    def mod(self, event=None):
        #a modification calls this function. the flag adressed by edit_modified() is set to True
        # The modification is handled by this function and the modified flag is set back to False by edit_modified(False)
        #problem is that the set back to False also triggers a modification event with flag set to False
        #so we have to check at the beginning whether the flag is True or False, otherwise we get two events for a keystroke

        if self.edit_modified():

            print("modified event at: {}, flag is {}".format(self.index(tk.INSERT), self.edit_modified()))
            print("Sentinel: {}".format(self.index("sentinel")))
            print("Visible lines: {}".format(self.visible_lines()))
            self.edit_modified(False)

        self.mark_set("sentinel", tk.INSERT)


    def key_pressed(self, event=None):
        print("key pressed at: {}".format(self.index(tk.INSERT)))
        a = float(self.index(tk.INSERT))
        print(a)

    def visible_lines(self):
        #returns the lines visible in the text widget. returns (index of first visible position, index of last visible position)
        start = self.index("@0,0")
        #print("@{},{}".format(self.winfo_height(), self.winfo_width()))
        end = self.index("@{},{}".format(self.winfo_height(), self.winfo_width()))
        return (start, end)

if __name__ == '__main__':
    c = tk.Tk()
    t = TestText(c)
    t.pack(side=tk.TOP, fill=tk.BOTH, expand=1)
    c.mainloop()