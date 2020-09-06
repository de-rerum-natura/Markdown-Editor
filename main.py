# This is a sample Python script.

# Press Umschalt+F10 to execute it or replace it with your code.
# Press Double Shift to search everywhere for classes, files, tool windows, actions, and settings.

import tkinter as tk
from tkinter import filedialog
import tkinter.ttk as ttk
from PPFileBrowser import PPFileBrowser
from PPEditor import PPEditor
from PPTreeBrowser import PPTreeBrowser
from PPOutlineBrowser import PPOutlineBrowser
from PPLineNumbers import PPLineNumbers
from PPStyle import PPStyle
import os
import json


class MainWindow(tk.Tk):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.configurations = self.load_config()

        self.title('Peters Editor')
        #self.geometry('1000x500')

        self.foreground = 'black'
        self.background = 'lightgrey'
        self.text_foreground = 'black'
        self.text_background = 'white'

        self.open_file = ''
        self.right_frame_visible = True

        # define editor area and scrollbars
        self.editor = PPEditor(self, 'style.json')
        self.editor_vsb = ttk.Scrollbar(self, orient='vertical', command=self.editor.yview)
        #self.editor_hsb = ttk.Scrollbar(self.left_frame, orient='horizontal', command=self.editor.xview)
        self.editor.configure(yscrollcommand=self.editor_vsb.set)

        #define the Line numbers canvas
        #self.line_numbers = PPLineNumbers(self.left_frame, self.editor, width=30, background = "white", borderwidth=0, relief="flat")

        # define file browser and editor_vsbs
        #self.vsb = ttk.Scrollbar(self.right_frame, orient="vertical")
        #self.hsb = ttk.Scrollbar(self.right_frame, orient="horizontal")
        #self.file_browser = PPFileBrowser(self.right_frame, yscrollcommand=self.vsb.set, xscrollcommand=self.hsb.set)
        #self.vsb['command'] = self.file_browser.yview
        #self.hsb['command'] = self.file_browser.xview

        #define tree brower
        self.vsb = ttk.Scrollbar(self, orient="vertical")
        self.hsb = ttk.Scrollbar(self, orient="horizontal")
        self.tree_browser = PPTreeBrowser(self, yscrollcommand=self.vsb.set, xscrollcommand=self.hsb.set)
        self.vsb['command'] = self.tree_browser.yview
        self.hsb['command'] = self.tree_browser.xview

        #define the outline browser
        self.ovsb = ttk.Scrollbar(self, orient="vertical")
        self.ohsb = ttk.Scrollbar(self, orient="horizontal")
        self.outline_browser = PPOutlineBrowser(self, self.editor, yscrollcommand=self.vsb.set, xscrollcommand=self.hsb.set)
        self.ovsb['command'] = self.outline_browser.yview
        self.ohsb['command'] = self.outline_browser.xview

        #define the label bar
        self.status_bar_var = tk.StringVar()
        self.status_bar = tk.Label(self, textvariable=self.status_bar_var, anchor = "w", relief=tk.RAISED)
        self.status_bar_var.set("Test")

        # define menu
        self.menu = tk.Menu(self, bg=self.background, fg=self.foreground)
        self.all_menus = [self.menu]

        sub_menu_items = ["file", "edit", "tools", "help"]
        self.generate_sub_menus(sub_menu_items)
        self.configure(menu=self.menu)

        self.right_click_menu = tk.Menu(self, bg=self.background, fg=self.foreground, tearoff=0)
        self.right_click_menu.add_command(label='Cut', command=self.edit_cut)
        self.right_click_menu.add_command(label='Copy', command=self.edit_copy)
        self.right_click_menu.add_command(label='Paste', command=self.edit_paste)
        self.all_menus.append(self.right_click_menu)

        # pack editor area
        #self.line_numbers.pack(side=tk.LEFT, fill=tk.Y)
        #self.editor_hsb.pack(side=tk.BOTTOM, fill=tk.X)
        self.editor.grid(row=0, column=0, sticky="nsew")
        self.editor_vsb.grid(row=0, column=1, sticky="ns")
        self.editor.set_style()

        # pack browser / tree browser area
        self.tree_browser.grid(row=0, column=2, sticky='nsew')
        self.vsb.grid(row=0, column=3, sticky='ns')
        self.hsb.grid(row=1, column=2, sticky='ew')

        self.status_bar.grid(row=2, column=0, sticky='ew')


        self.bind_events()

        #if a file is saved in config, load it into the editor
        if (self.configurations) and 'filename' in self.configurations:
            self.editor.display_file_contents(self.configurations['filename'])



    def bind_events(self):
        self.bind("<<PPFileChosen>>", self.openFile)
        self.bind("<<PPNodeChosen>>", self.highlight_span)
        self.bind("<<PPEditorReparsed>>", self.update_treeview)
        #self.bind("LineNumbers", self.line_numbers.redraw())
        self.protocol("WM_DELETE_WINDOW", self.on_closing)


    def load_config(self):
        configurations = {}
        if os.path.exists('config.json'):
            with open('config.json', 'r') as f:
                configurations = json.load(f)
        return configurations

    def save_config(self):
        if self.configurations:
            if os.path.exists('config.json'):
                os.remove('config.json')
            with open('config.json', 'w') as f:
                json.dump(self.configurations, f)

    # def.configure_styles(self):
    #    style = ttk.Style()

    #highlight span
    def highlight_span(self, event):
        self.editor.highlight_span(self.tree_browser.span)

    #update the treeview if editor reparsed content
    def update_treeview(self, event):
        print("update treeview")
        self.tree_browser.update_tree(self.editor.parser.tree)
        self.editor.highlighter.highlight()
        self.outline_browser.update_tree()

    # Menu functions
    def show_right_click_menu(self, event):
        x = self.winfo_x() + self.text_area.winfo_x() + event.x
        y = self.winfo_y() + self.text_area.winfo_y() + event.y
        self.right_click_menu.post(x, y)

    def generate_sub_menus(self, sub_menu_items):
        window_methods = [method_name for method_name in dir(self)
                          if callable(getattr(self, method_name))]
        tkinter_methods = [method_name for method_name in dir(tk.Tk)
                           if callable(getattr(tk.Tk, method_name))]

        my_methods = [method for method in set(window_methods) - set(tkinter_methods)]
        my_methods = sorted(my_methods)

        for item in sub_menu_items:
            sub_menu = tk.Menu(self.menu, tearoff=0, bg=self.background, fg=self.foreground)
            matching_methods = []
            for method in my_methods:
                if method.startswith(item):
                    matching_methods.append(method)

            for match in matching_methods:
                actual_method = getattr(self, match)
                method_shortcut = actual_method.__doc__.strip()
                friendly_name = ' '.join(match.split('_')[1:])
                sub_menu.add_command(label=friendly_name.title(), command=actual_method, accelerator=method_shortcut)

            self.menu.add_cascade(label=item.title(), menu=sub_menu)
            self.all_menus.append(sub_menu)

    def openFile(self, event):
        self.open_file = self.file_browser.path
        self.editor.display_file_contents(self.file_browser.path)

    def highlight_span(self, span):
        self.editor.highlight_span(self.tree_browser.span)

    # =========== Menu Functions ==============

    def file_new(self, event=None):
        """
        Ctrl+N
        """
        self.editor.delete(1.0, tk.END)
        self.open_file = None

    def file_open(self, event=None):
        """
        Ctrl+O
        """
        file_to_open = filedialog.askopenfilename()
        if file_to_open:
            self.open_file = file_to_open
            self.configurations['filename'] = file_to_open
            self.editor.display_file_contents(file_to_open)
            self.tree_browser.update_tree(self.editor.parser.tree)


    def file_save(self, event=None):
        """
        Ctrl+S
        """
        current_file = self.open_file if self.open_file else None
        if not current_file:
            current_file = filedialog.asksaveasfilename()

        if current_file:
            contents = self.editor.get(1.0, tk.END)
            with open(current_file, 'w') as file:
                file.write(contents)
            self.configurations['filename'] = current_file

    def edit_cut(self, event=None):
        """
        Ctrl+X
        """
        self.editor.event_generate("<Control-x>")

    def edit_paste(self, event=None):
        """
        Ctrl+V
        """
        self.editor.event_generate("<Control-v>")

    def edit_copy(self, event=None):
        """
        Ctrl+C
        """
        self.editor.event_generate("<Control-c>")

    def edit_select_all(self, event=None):
        """
        Ctrl+A
        """
        self.editor.event_generate("<Control-a>")

    def edit_find_and_replace(self, event=None):
        """
        Ctrl+F
        """
        # self.show_find_window()

    def help_about(self, event=None):
        """
        Ctrl+H
        """
        # self.show_about_page()

    def tools_toggle_directory_pane(self, event=None):
        """
        Ctrl+M
        """
        if self.right_frame_visible:
            self.right_frame_visible = False
            self.right_frame.pack_forget()
        else:
            self.right_frame_visible = True
            self.right_frame.pack(side=tk.RIGHT, fill=tk.Y)

    def on_closing(self):
        self.save_config()
        self.destroy()

if __name__ == '__main__':
    c = MainWindow()

    c.mainloop()
