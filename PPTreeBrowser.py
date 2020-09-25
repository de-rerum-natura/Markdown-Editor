# -*- coding: utf-8 -*-
"""
Created on Aug 04 2020

@author: Peter
"""

from tree_sitter import Language, Parser
import tkinter.ttk as ttk
import PPUtils


class PPTreeBrowser(ttk.Treeview):
    def __init__(self, master, editor, **kwargs):
        super().__init__(master, **kwargs)
        #self['columns'] = ("fname")
        #self['displaycolumns'] = "size"
        self['columns'] = ("start_index", "end_index")
        self['displaycolumns'] = ""
        self.heading("#0", text="Type", anchor='w')
        #self.heading("fname", text="FieldName", anchor='w')
        #self.heading("named", text="Named", anchor='w')
        #self.heading("start", text="Start", anchor='w')
        #self.heading("end", text="End", anchor='w')
        #self.heading("canonical", text="start byte", anchor='w')
        #self.heading("endbyte", text="end byte", anchor='w')
        #self.heading("ttkID", text="ttkID", anchor='w')
        #self.column("ttkID", stretch=0, width=50)

        #self.bind('<<TreeviewOpen>>', self.update_tree)
        #self.bind('<Double-Button-1>', self.change_dir)
        #self.bind("<<PPEditorReparsed>>", self.update_tree)

        self.editor=editor
        self.span = ["0.0", "end"]
        self.id_counter = 0

        self.bind('<Double-Button-1>', self.node_selected)

        self.root_node = ""

    def point_convert(self, point):
        #conversion for tk text widget. lines start with 1 instead of 0
        line = point[0]+1
        return "{}.{}".format(line, point[1])

    def node_id(self, node):
        return "{}.{}.{}".format(node.type, node.start_byte, node.end_byte)


    def recursiveTreeWalk(self, parentID, node):
        if parentID == 0:
            #self.insert('', 0, self.node_id(node), text=node.type, values=[node.sexp(), node.is_named, self.point_convert(node.start_point), self.point_convert(node.end_point), node.start_byte, node.end_byte, self.node_id(node)])
            start_index = PPUtils.convert_point_ts_to_tk(node.start_point)
            end_index = PPUtils.convert_point_ts_to_tk(node.end_point)
            self.insert('', 0, self.node_id(node), text=node.type, values=[start_index, end_index])
        else:
            #self.insert(parentID, 'end', self.node_id(node), text=node.type, values=[node.sexp(), node.is_named, self.point_convert(node.start_point), self.point_convert(node.end_point), node.start_byte, node.end_byte, self.node_id(node)])
            start_index = PPUtils.convert_point_ts_to_tk(node.start_point)
            end_index = PPUtils.convert_point_ts_to_tk(node.end_point)
            self.insert(parentID, 'end', self.node_id(node), text=node.type, values=[start_index, end_index])
        if len(node.children) > 0:
            for child in node.children:
                self.recursiveTreeWalk(self.node_id(node), child)

    def open_children(self, parent):
        self.item(parent, open=True)
        for child in self.get_children(parent):
            self.open_children(child)

    def update_tree(self, tree):
        #print("treeviewupdate")
        self.delete(*self.get_children())
        self.root_node = self.node_id(tree.root_node)
        self.recursiveTreeWalk(0, tree.root_node)
        self.item(self.root_node, open=True)
        #self.open_children(self.node_id(tree.root_node))
        self.focus()

    def node_selected(self, event):
        node = self.focus()
        begin_pos = self.set(node, "start_index")
        end_pos = self.set(node, "end_index")
        self.editor.see(begin_pos)
        self.editor.tag_remove('sel', '1.0', 'end')
        self.editor.tag_add('sel', begin_pos, end_pos)
        self.editor.mark_set("insert", end_pos)
        self.editor.focus_set()

    def look_for_index(self, index):
        parent = self.root_node
        float_index = float(index)
        for child in self.get_children(parent):
            begin_pos = float(self.set(child, "start"))
            end_pos = float(self.set(child, "end"))
            if (float_index > begin_pos) and (float_index < end_pos):
                self.focus(child)
                self.open_children(child)
                return

