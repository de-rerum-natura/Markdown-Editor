# This is a sample Python script.

# Press Umschalt+F10 to execute it or replace it with your code.
# Press Double Shift to search everywhere for classes, files, tool windows, actions, and settings.

import tkinter as tk
from tkinter import filedialog
import tkinter.ttk as ttk
from PPEditor import PPEditor
from PPTreeBrowser import PPTreeBrowser
from PPOutlineBrowser import PPOutlineBrowser
from PPEditorStyle import PPEditorStyle
from PPCodeStyle import PPCodeStyle
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

        #define styles:
        self.editor_style = PPEditorStyle()
        self.code_style = PPCodeStyle()

        #define the paned window
        self.panes = tk.PanedWindow()
        self.panes.pack(fill=tk.BOTH, expand=1)

        # define editor area and scrollbars
        self.editor_frame = tk.Frame()
        self.editor = PPEditor(self.editor_frame, self.code_style)
        self.editor_vsb = ttk.Scrollbar(self.editor_frame, orient='vertical', command=self.editor.yview)
        self.editor.configure(yscrollcommand=self.editor_vsb.set)

        self.editor.pack(side=tk.LEFT, fill=tk.BOTH, expand=1)
        self.editor_vsb.pack(side=tk.RIGHT, fill=tk.Y)
        self.panes.add(self.editor_frame)
        # define the notebook

        self.notebook = ttk.Notebook(self)
        self.frame_one = ttk.Frame(self.notebook)
        self.frame_two = ttk.Frame(self.notebook)

        # define the outline browser
        self.ovsb = ttk.Scrollbar(self.frame_two, orient="vertical")
        self.outline_browser = PPOutlineBrowser(self.frame_two, self.editor, yscrollcommand=self.ovsb.set)
        self.ovsb['command'] = self.outline_browser.yview
        self.notebook.add(self.frame_two, text="Outline")

        # define tree brower
        self.tvsb = ttk.Scrollbar(self.frame_one, orient="vertical")
        self.tree_browser = PPTreeBrowser(self.frame_one, self.editor, yscrollcommand=self.tvsb.set)
        self.tvsb['command'] = self.tree_browser.yview
        self.notebook.add(self.frame_one, text="Elements")

        # notebook outline browser / tree browser area

        self.ovsb.pack(side=tk.RIGHT, fill=tk.Y)
        self.outline_browser.pack(side=tk.TOP, fill=tk.BOTH, expand=1)

        self.tvsb.pack(side=tk.RIGHT, fill=tk.Y)
        self.tree_browser.pack(side=tk.LEFT, fill=tk.BOTH, expand=1)

        self.panes.add(self.notebook)


        # define menu
        self.menu = tk.Menu(self, bg=self.background, fg=self.foreground)
        self.all_menus = [self.menu]

        #sub_menu_items = ["file", "edit", "tools", "help"]
        #self.generate_sub_menus(sub_menu_items)
        self._generate_sub_menus()
        self.configure(menu=self.menu)

        self.right_click_menu = tk.Menu(self, bg=self.background, fg=self.foreground, tearoff=0)
        self.right_click_menu.add_command(label='Cut', command=self.edit_cut)
        self.right_click_menu.add_command(label='Copy', command=self.edit_copy)
        self.right_click_menu.add_command(label='Paste', command=self.edit_paste)
        self.all_menus.append(self.right_click_menu)

        self.bind_events()

        #if a file is saved in config, load it into the editor
        if (self.configurations) and 'filename' in self.configurations:
            self.editor.display_file_contents(self.configurations['filename'])



    def bind_events(self):
        self.bind("<<PPFileChosen>>", self.openFile)
        self.bind("<<PPOutlineNodeChosen>>", self.highlight_span)
        self.bind("<<PPEditorReparsed>>", self.update_treeview)
        self.bind("<Control-i>", self.insert_unicode)
        self.protocol("WM_DELETE_WINDOW", self.on_closing)


    def insert_unicode(self, event=None):
        self.editor.insert(tk.INSERT, u"\u2502")

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
        print("here")
        self.editor.highlight_span(self.outline_browser.span)

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

    def _generate_sub_menus(self):
        file_sub_menu = tk.Menu(self.menu, tearoff=0, bg=self.background, fg=self.foreground)
        file_sub_menu.add_command(label='New', command=self.file_new, accelerator='Ctrl+N')
        file_sub_menu.add_command(label='Open', command=self.file_open, accelerator='Ctrl+O')
        file_sub_menu.add_command(label='Save', command=self.file_save, accelerator='Ctrl+S')
        file_sub_menu.add_command(label='Export', command=self.file_export, accelerator='Ctrl+E')
        self.menu.add_cascade(label='File', menu=file_sub_menu)
        self.all_menus.append(file_sub_menu)

        edit_sub_menu = tk.Menu(self.menu, tearoff=0, bg=self.background, fg=self.foreground)
        edit_sub_menu.add_command(label='Cut', command=self.edit_cut, accelerator='Ctrl+X')
        edit_sub_menu.add_command(label='Copy', command=self.edit_copy, accelerator='Ctrl+C')
        edit_sub_menu.add_command(label='Paste', command=self.edit_paste, accelerator='Ctrl+V')
        edit_sub_menu.add_command(label='Select all', command=self.edit_select_all, accelerator='Ctrl+A')
        edit_sub_menu.add_command(label='Find and replace', command=self.edit_find_and_replace, accelerator='Ctrl+F')
        self.menu.add_cascade(label='Edit', menu=edit_sub_menu)
        self.all_menus.append(edit_sub_menu)

        view_sub_menu = tk.Menu(self.menu, tearoff=0, bg=self.background, fg=self.foreground)
        view_sub_menu.add_command(label='Editor Style', command=self.tools_editor_style)
        view_sub_menu.add_command(label='Code Style', command=self.tools_code_style)
        self.menu.add_cascade(label='View', menu=view_sub_menu)
        self.all_menus.append(view_sub_menu)


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

    def file_export(self, event=None):
        """
        Ctrl+E
        """
        acceptable_types = {'html', 'HTML', 'pdf', 'PDF', 'docx', 'DOCX'}
        export_file = filedialog.asksaveasfilename(filetypes = [('Html', '*.htm'), ('Docx', '*.docx'), ('Pdf','*.pdf')])
        if export_file:
            ext = export_file.split('.')[-1]
            print(ext)
            if ext == 'htm':
                ext = 'html'
            if ext in acceptable_types:
                self.editor.export(ext, export_file)

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

    def tools_editor_style(self, event=None):
        self.editor.set_style(self.editor_style)

    def tools_code_style(self, event=None):
        self.editor.set_style(self.code_style)

    def on_closing(self):
        self.save_config()
        self.destroy()

if __name__ == '__main__':
    c = MainWindow()

    c.mainloop()
