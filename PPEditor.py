# -*- coding: utf-8 -*-
"""
Created on Wed Jul 29 15:12:38 2020

@author: Peter
"""
import tkinter as tk
import tkinter.ttk as ttk
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

        #Flags
        self.ret_active=False

    def bind_events(self):
        super().bind_events()
        self.bind('<Control-h>', self.highlight)
        self.bind('<Control-p>', self.print_position)
        self.bind('<Key>', self.key_pressed)
        self.bind('<<Modified>>', self.mod)
        self.bind('<space>', self.space_pressed)
        self.bind('<Return>', self.return_pressed)
        #self.bind('<KeyRelease-Return>', self.return_released)


    def print_position(self, event=None):
        print(self.tag_names(self.index(tk.INSERT)))

    def show_position(self, index):
        return self.tag_names(index)


    def highlight(self, event=None):
        self.highlighter.highlight()
        return "break"

    def key_pressed(self, event=None):
        self.mark_set("sentinel", tk.INSERT)


    def space_pressed(self, event=None):
        #re-parse the whole document and tell the world that the editor was parsed
        self.parser.re_parse(self.get('1.0', 'end'))
        self.event_generate("<<PPEditorReparsed>>")

    def return_pressed(self, event=None):
        #if we just inserted an auto inserted text and Return is pressed immediately afterwards, delete the text again
        if 'auto_inserted' in self.tag_names(tk.INSERT + "-1c"):
            self.delete(self.index(tk.INSERT) + " linestart", self.index(tk.INSERT) + " lineend")
            return "break"
        # re-parse the whole document and tell the world that the editor was parsed
        self.ret_active=True
        self.parser.re_parse(self.get('1.0', 'end'))
        self.event_generate("<<PPEditorReparsed>>")


    def mod(self, event=None):
        #a modification calls this function via the <<Modified>> event. the flag adressed by edit_modified() is set to True
        # The modification is handled by this function and the modified flag is set back to False by edit_modified(False)
        #problem is that the set back to False also triggers a modification event with flag set to False
        #so we have to check at the beginning whether the flag is True or False, otherwise we get two events for a keystroke

        if self.edit_modified():
            print("modified event at: {}, flag is {}".format(self.index(tk.INSERT), self.edit_modified()))

            if self.parser.tree != None:

                s = self.index("sentinel")
                e = self.index(tk.INSERT)
                print("Tk StartIndex: {}, EndIndex: {}".format(s,e))

                #do editing if required
                if self.ret_active:
                    print("caugt return")
                    #todo index not correct
                    print(self.tag_nextrange('list_paragraph', e + " - 1line linestart", e + " - 1line lineend"))
                    if self.tag_nextrange('list_paragraph', e + " - 1line linestart", e + " - 1line lineend"):
                        self.insert(e,"* ", "auto_inserted")
                        e = self.index(tk.INSERT)
                    self.ret_active=False

                # tk start index was regisered at key press before tk text widget processes text.
                # make sure that it is smaller than the insert position (required for ts). otherwise switch

                if self.compare(s, "<=", e):
                    start_index = my_utils.convert_point_tk_to_ts(s)
                    end_index = my_utils.convert_point_tk_to_ts(e)
                else:
                    start_index = my_utils.convert_point_tk_to_ts(e)
                    end_index = my_utils.convert_point_tk_to_ts(s)

                # start byte is based on the tk start index, end byte on the current index
                #todo maybe make this more efficient by reducing need to calculate end_byte.
                #if start_index[0]==current_index[0] then start_byte + (current_index[1]-start_index[1])?
                #may be faster?
                start_byte = self.convert_index_to_canonical(self.index("sentinel"))
                end_byte = self.convert_index_to_canonical((self.index(tk.INSERT)))

                print("StartIndex: {}, EndIndex: {}, start byte: {}, end byte: {}".format(start_index, end_index,
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

            #set the sentinel to the new tk.INSERT position
            self.mark_set("sentinel", tk.INSERT)
            #set the modified flag to false
            self.edit_modified(False)

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


