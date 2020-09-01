# -*- coding: utf-8 -*-
"""
Created on Wed Jul 29 15:12:38 2020

@author: Peter
"""
import tkinter as tk
import tkinter.ttk as ttk
import re
from PPParser import PPParser
from PPHighlighter import PPHighlighter
import PPUtils as my_utils
from PPStyle import PPStyle
from enhancedtext import Enhanced_Text

class PPEditor(Enhanced_Text):
    def __init__(self, master, style_path, **kwargs):
        super().__init__(master, **kwargs)
        
        self.master = master

        #highlight settings
        self.tag_configure('highlight', background= 'yellow')

        #Parser
        self.parser = PPParser()

        #Style
        # read in the style and configure the standard style of the editor as well as the highlight tags
        self.style = PPStyle(style_path)
        self.style.apply_style_to(self)

        #Highlighter
        self.highlighter = PPHighlighter(self,self.style.queries)

        #Events
        self.bind_events()

        #set the sentinel for tk.INSERT
        self.mark_set("sentinel", tk.INSERT)
        self.mark_gravity("sentinel", tk.LEFT)

        #Tags
        self.tag_configure("auto_inserted", foreground='grey20')

        #Whitespace characters:
        self.INLINECHARS = {"*", "`"}
        self.WHITESPACE = {" ", "\t"}
        self.BRACKETS = {"[" : "]", "(" : ")", "{" : "}", '"' : '"'}

        #regex for list marker
        self._list_marker_re = re.compile(r'[ \t]*[*-+][ \t]*')

    def bind_events(self):
        super().bind_events()
        self.bind('<Control-h>', self.highlight)
        self.bind('<Control-p>', self.print_position)
        self.bind('<Key>', self.key_pressed)
        self.bind('<<TextChanged>>', self.mod)
        self.bind('<space>', self.space_pressed)
        self.bind('<Return>', self.return_pressed)
        self.bind('<Control-w>', self.select_word)
        self.bind('<Control-e>', self.insert_emphasis)
        #self.bind('<KeyRelease-Return>', self.return_released)

    def key_pressed(self, event=None):
        if event.char in self.INLINECHARS:
            before = self.get(tk.INSERT + " -1c", tk.INSERT)
            after = self.get(tk.INSERT, tk.INSERT + " +1c")
            if before in self.WHITESPACE:
                if after in self.WHITESPACE:
                    self.insert(tk.INSERT, event.char*2)
                    self.mark_set(tk.INSERT, tk.INSERT + " -1c")
                    return "break"
            if before == event.char:
                if self.get(tk.INSERT + " -2c", tk.INSERT + " -1c") == event.char:
                    #self.insert(tk.INSERT, event.char)
                    return "break"
                if after == event.char:
                    self.insert(tk.INSERT, event.char*2)
                    self.mark_set(tk.INSERT, tk.INSERT + " -1c")
                    return "break"

        if event.char in self.BRACKETS:
            self.insert(tk.INSERT, event.char + self.BRACKETS[event.char])
            self.mark_set(tk.INSERT, tk.INSERT + " -1c")
            return "break"


    def insert_emphasis(self, event=None):
        first, last = self.get_selection_indices()
        selection=False
        if first and last:
            last = last + " +1c"
            selection=True
        else:
            first = tk.INSERT + " wordstart"
            last = tk.INSERT + " wordend"

        if self.get(first + " -2c", first) != "**":
            self.insert(first, "*")
            self.insert(last, "*")
            self.re_parse()
            if selection:
                self.tag_add(tk.SEL, first + " +1c", last)
                self.mark_set(tk.INSERT, last)
        return "break"

    def print_position(self, event=None):
        print(self.tag_names(self.index(tk.INSERT)))

    def highlight(self, event=None):
        self.highlighter.highlight()
        return "break"

    def re_parse(self):
        self.parser.re_parse(self.get('1.0', 'end'))
        self.event_generate("<<PPEditorReparsed>>")

    def space_pressed(self, event=None):
        #delete selection, if present
        first, last = self.get_selection_indices()
        if first and last:
            self.delete(first, last)
            self.mark_set("insert", first)
        #insert space
        self.insert(tk.INSERT, " ")
        #re-parse the document
        self.re_parse()
        return "break"


    def return_pressed(self, event=None):
        #delete selection, if present
        first, last = self.get_selection_indices()
        if first and last:
            self.delete(first, last)
            self.mark_set("insert", first)

        #if we just inserted an auto inserted text and Return is pressed immediately afterwards, delete the text again
        if 'auto_inserted' in self.tag_names(tk.INSERT + "-1c"):
            self.tag_remove('auto_inserted', tk.INSERT + " -1 line linestart", tk.INSERT + " lineend")
            self.delete(tk.INSERT + " linestart", tk.INSERT + " lineend")
            return "break"

        #if the line contains a list_paragraph, search for the previous list marker and insert it, mark it auto_inserted
        if self.tag_nextrange('list_paragraph', tk.INSERT + " linestart", tk.INSERT + " lineend"):
            i1, i2 = self.tag_prevrange('list_marker',tk.INSERT, '1.0')
            list_char = self.get(i1, i2)
            self.insert(tk.INSERT, f"\n{list_char} ", "auto_inserted")
            return "break"

        #if we are in an indented code block, insert the indentation of the current line in the next line
        if self.get_line_indent(tk.INSERT) >= 4:
            no_of_indent_chars = self.get_line_indent(tk.INSERT)-1
            self.insert(tk.INSERT, f"\n{' '*no_of_indent_chars} ", "auto_inserted")
            return "break"

        #default. insert a return and reparse the document
        self.insert(tk.INSERT, "\n")
        self.re_parse()
        return "break"


    def mod(self, event=None):

        if self.parser.tree != None:

            start_index = my_utils.convert_point_tk_to_ts(self.last_change_range[0])
            end_index = my_utils.convert_point_tk_to_ts(self.last_change_range[1])

            # start byte is based on the tk start index, end byte on the current index
            #todo maybe make this more efficient by reducing need to calculate end_byte.
            #if start_index[0]==current_index[0] then start_byte + (current_index[1]-start_index[1])?
            #may be faster?
            start_byte = self.convert_index_to_canonical(self.last_change_range[0])
            end_byte = self.convert_index_to_canonical(self.last_change_range[1])

            print("Inserting into tree: startIndex: {}, endIndex: {}, start byte: {}, end byte: {}".format(start_index, end_index,
                                                                                      start_byte, end_byte))

            # edit the tree sitter tree held in the parser
            self.parser.edit_tree(
                start_byte=start_byte,
                old_end_byte=start_byte,
                new_end_byte=end_byte,
                start_point=start_index,
                old_end_point=start_index,
                new_end_point=end_index,
            )


    def display_file_contents(self, filepath):
        #add the parsing and highlighting of the document
        super().display_file_contents(filepath)
        self.parser.parse(self.get('1.0', 'end'))
        self.event_generate("<<PPEditorReparsed>>")
        self.highlight()

    def highlight_span(self, span):
        #highlight a span
        self.tag_remove('highlight', 1.0, tk.END)
        self.tag_add('highlight', span[0], span[1])
        self.see(span[0])


