# -*- coding: utf-8 -*-
"""
Created on Tue Jul 21 14:45:59 2020

@author: Peter
"""

import os
import glob
import tkinter as tk
import tkinter.ttk as ttk

class FileBrowser(tk.Frame):
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)
        
        self.vsb = ttk.Scrollbar(orient="vertical")
        self.hsb = ttk.Scrollbar(orient="horizontal")
        
     
        self.tree = ttk.Treeview(columns=("fullpath", "type", "size"), displaycolumns="size", yscrollcommand=self.vsb.set, xscrollcommand=self.hsb.set)
        self.vsb['command'] = self.tree.yview
        self.hsb['command'] = self.tree.xview

        self.tree.heading("#0", text="Directory Structure", anchor='w')
        self.tree.heading("size", text="File Size", anchor='w')
        self.tree.column("size", stretch=0, width=100)    
        
        self.populate_roots(self.tree)
        self.tree.bind('<<TreeviewOpen>>', self.update_tree)
        self.tree.bind('<Double-Button-1>', self.change_dir)
        
        
        
    def packItems(self):
        
        self.vsb.pack(side=tk.RIGHT, fill=tk.Y)
        self.hsb.pack(side=tk.BOTTOM, fill=tk.Y)
        self.tree.pack(side=tk.TOP, fill=tk.BOTH, expand=1)
  
    def autoscroll(self, sbar, first, last):
        """Hide and show scrollbar as needed."""
        first, last = float(first), float(last)
        if first <= 0 and last >= 1:
            sbar.pack_forget()
        else:
            sbar.pack()
        sbar.set(first, last)
        
    def populate_tree(self, tree, node):
        if tree.set(node, "type") != 'directory':
            return
    
        path = tree.set(node, "fullpath")
        tree.delete(*tree.get_children(node))
    
        parent = tree.parent(node)
        special_dirs = [] if parent else glob.glob('.') + glob.glob('..')
    
        for p in special_dirs + os.listdir(path):
            ptype = None
            p = os.path.join(path, p).replace('\\', '/')
            if os.path.isdir(p): ptype = "directory"
            elif os.path.isfile(p): ptype = "file"
    
            fname = os.path.split(p)[1]
            id = tree.insert(node, "end", text=fname, values=[p, ptype])
    
            if ptype == 'directory':
                if fname not in ('.', '..'):
                    tree.insert(id, 0, text="dummy")
                    tree.item(id, text=fname)
            elif ptype == 'file':
                size = os.stat(p).st_size
                tree.set(id, "size", "%d bytes" % size)


    def populate_roots(self, tree):
        dir = os.path.abspath('.').replace('\\', '/')
        node = tree.insert('', 'end', text=dir, values=[dir, "directory"])
        self.populate_tree(tree, node)
    
    def update_tree(self,event):
        tree = event.widget
        self.populate_tree(tree, tree.focus())
    
    def change_dir(self, event):
        tree = event.widget
        node = tree.focus()
        if tree.parent(node):
            path = os.path.abspath(tree.set(node, "fullpath"))
            if os.path.isdir(path):
                os.chdir(path)
                tree.delete(tree.get_children(''))
                self.populate_roots(tree)
            else:
                message = "file selected: " + path
                self.master.status_area.configure(state='normal')
                self.master.status_area.delete(1.0, tk.END)
                self.master.status_area.insert(tk.END, message)
                self.master.status_area.configure(state='disabled')

        
#if __name__ == '__main__':
#    root = tk.Tk()
#    f = FileBrowser(root)
#    f.pack(side=tk.TOP, fill=tk.BOTH, expand=1)
#    root.mainloop()