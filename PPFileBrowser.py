# -*- coding: utf-8 -*-
"""
Created on Wed Jul 29 14:35:34 2020

@author: Peter
"""

import os
import glob
import tkinter.ttk as ttk

class PPFileBrowser(ttk.Treeview):
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)
        self['columns'] = ("fullpath", "type", "size")
        self['displaycolumns'] = "size"
        
        self.heading("#0", text="Directory Structure", anchor='w')
        self.heading("size", text="File Size", anchor='w')
        self.column("size", stretch=0, width=100)
        
        self.populate_roots()
        self.bind('<<TreeviewOpen>>', self.update_tree)
        self.bind('<Double-Button-1>', self.change_dir)
        
        self.path = ''
        
        
    def populate_tree(self, node):
        if self.set(node, "type") != 'directory':
            return
    
        path = self.set(node, "fullpath")
        self.delete(*self.get_children(node))
    
        parent = self.parent(node)
        special_dirs = [] if parent else glob.glob('.') + glob.glob('..')
    
        for p in special_dirs + os.listdir(path):
            ptype = None
            p = os.path.join(path, p).replace('\\', '/')
            if os.path.isdir(p): ptype = "directory"
            elif os.path.isfile(p): ptype = "file"
    
            fname = os.path.split(p)[1]
            id = self.insert(node, "end", text=fname, values=[p, ptype])
    
            if ptype == 'directory':
                if fname not in ('.', '..'):
                    self.insert(id, 0, text="dummy")
                    self.item(id, text=fname)
            elif ptype == 'file':
                size = os.stat(p).st_size
                self.set(id, "size", "%d bytes" % size)


    def populate_roots(self):
        dir = os.path.abspath('.').replace('\\', '/')
        node = self.insert('', 'end', text=dir, values=[dir, "directory"])
        self.populate_tree(node)
    
    def update_tree(self,event):
        self.populate_tree(self.focus())
    
    def change_dir(self, event):
        node = self.focus()
        if self.parent(node):
            path = os.path.abspath(self.set(node, "fullpath"))
            if os.path.isdir(path):
                os.chdir(path)
                self.delete(self.get_children(''))
                self.populate_roots()
            else:
                self.path = path
                print(self.path)
                self.event_generate("<<PPFileChosen>>")
                
