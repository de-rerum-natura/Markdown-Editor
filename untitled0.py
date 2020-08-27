# -*- coding: utf-8 -*-
"""
Created on Tue Jul 21 10:53:24 2020

@author: Peter
"""


import tkinter as tk
from tkinter import filedialog
import tkinter.ttk as ttk
from PPFileBrowser import PPFileBrowser
from PPEditor import PPEditor



class MainWindow(tk.Tk):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.title('Peters Editor')
        self.geometry('1000x500')
        
        self.foreground = 'black'
        self.background = 'lightgrey'
        self.text_foreground = 'black'
        self.text_background='white'
        
        self.open_file = ''
        self.right_frame_visible = True
        
        #define frames
        self.right_frame = tk.Frame(self)
        self.left_frame = tk.Frame(self)
        self.bottom_frame = tk.Frame(self.left_frame)
        
        #define editor area and scrollbars
        self.editor_area = PPEditor(self.left_frame, bg='white', fg='black', width=30)
        self.editor_vsb = ttk.Scrollbar(self.left_frame, orient='vertical', command=self.editor_area.yview)
        self.editor_hsb = ttk.Scrollbar(self.left_frame, orient='horizontal', command=self.editor_area.xview)
        self.editor_area.configure(yscrollcommand=self.editor_vsb.set, xscrollcommand=self.editor_hsb.set)
        
      
        #define file browser and editor_vsbs
        self.vsb = ttk.Scrollbar(self.right_frame, orient="vertical")
        self.hsb = ttk.Scrollbar(self.right_frame, orient="horizontal") 
        self.file_browser = PPFileBrowser(self.right_frame, yscrollcommand=self.vsb.set, xscrollcommand=self.hsb.set)
        self.vsb['command'] = self.file_browser.yview
        self.hsb['command'] = self.file_browser.xview
        
        
        #define menu
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
        
        #pack editor area
        self.left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=1)
        self.editor_vsb.pack(side=tk.RIGHT, fill=tk.Y)
        self.editor_hsb.pack(side=tk.BOTTOM, fill=tk.X)
        self.editor_area.pack(side=tk.TOP, fill=tk.BOTH, expand=1)
        
        #pack file browser area
        self.right_frame.pack(side=tk.RIGHT, fill=tk.Y)
        self.vsb.pack(side=tk.RIGHT, fill=tk.Y)
        self.hsb.pack(side=tk.BOTTOM, fill=tk.X)
        self.file_browser.pack(side=tk.TOP , fill=tk.BOTH, expand=1)
        
        
        self.bind_events()
    
    def bind_events(self):
        self.bind("<<PPFileChosen>>", self.openFile)
        
    #def.configure_styles(self):
    #    style = ttk.Style()
    
    #Menu functions
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
        self.editor_area.display_file_contents(self.file_browser.path)
        
      
     # =========== Menu Functions ==============

    def file_new(self, event=None):
        """
        Ctrl+N
        """
        self.editor_area.delete(1.0, tk.END)
        self.open_file = None

    def file_open(self, event=None):
        """
        Ctrl+O
        """
        file_to_open = filedialog.askopenfilename()
        if file_to_open:
            self.open_file = file_to_open
            self.editor_area.display_file_contents(file_to_open)
            

    def file_save(self, event=None):
        """
        Ctrl+S
        """
        current_file = self.open_file if self.open_file else None
        if not current_file:
            current_file = filedialog.asksaveasfilename()

        if current_file:
            contents = self.editor_area.get(1.0, tk.END)
            with open(current_file, 'w') as file:
                file.write(contents)

    def edit_cut(self, event=None):
        """
        Ctrl+X
        """
        self.editor_area.event_generate("<Control-x>")

    def edit_paste(self, event=None):
        """
        Ctrl+V
        """
        self.editor_area.event_generate("<Control-v>")

    def edit_copy(self, event=None):
        """
        Ctrl+C
        """
        self.editor_area.event_generate("<Control-c>")

    def edit_select_all(self, event=None):
        """
        Ctrl+A
        """
        self.editor_area.event_generate("<Control-a>")

    def edit_find_and_replace(self, event=None):
        """
        Ctrl+F
        """
        #self.show_find_window()

    def help_about(self, event=None):
        """
        Ctrl+H
        """
        #self.show_about_page()

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

    

if __name__ == '__main__':
    c = MainWindow()
    c.mainloop()

        