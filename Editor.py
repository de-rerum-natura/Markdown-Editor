# -*- coding: utf-8 -*-
"""
Created on Wed Jul 22 10:02:58 2020

@author: Peter
"""


import tkinter as tk
import tkinter.ttk as ttk

class Editor(tk.Frame):
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)
        
        self.editor_area = tk.Text(self, bg='white', fg='black', width = 30)
        self.scrollbar = ttk.Scrollbar(self, orient='vertical', command=self.editor_area.yview)
        self.editor_area.configure(yscrollcommand=self.scrollbar.set)
        
        self.scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.editor_area.pack(side=tk.TOP, fill=tk.BOTH, expand=1)
        
        