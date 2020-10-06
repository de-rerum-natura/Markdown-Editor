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
from PPEditorStyle import PPEditorStyle
from PPCodeStyle import PPCodeStyle
from enhancedtext import *
import webbrowser
from PPExporter import PPExporter

class PPEditor(Enhanced_Text):
    def __init__(self, master, style, *args, **kwargs):
        super().__init__(master, *args, **kwargs)
        
        self.master = master

        #highlight settings
        self.tag_configure('highlight', background= 'yellow')

        #Parser
        self.parser = PPParser()

        #Style and Highlighter
        self.style = style
        self.highlighter = PPHighlighter(self, self.style.queries)
        self.style.apply_style_to(self)

        #Exporter
        self.exporter = PPExporter()

        #Events
        self._bind_events()

        #special characters:
        self.LISTCHARS = {"*", "-", "+"}
        self.INLINECHARS = {"*", "_", "`"}
        self.WHITESPACE = {" ", "\n", "\t"}
        self.BRACKETS = {"[" : "]", "(" : ")", "{" : "}", '"' : '"'}

        #regex for list marker
        self._list_marker_re = re.compile(r'[ \t]*[*-+][ \t]*')

        #ignore insert
        self.mod_ignore=False


    def set_style(self, style):
        self.style = style
        self.highlighter = PPHighlighter(self, self.style.queries)
        self.style.apply_style_to(self)
        self.highlight()

    def _bind_events(self):
        super()._bind_events()
        self.bind('<Control-h>', self.highlight)
        self.bind('<Control-p>', self.print_position)
        self.bind('<Key>', self._key_pressed)
        self.bind('<<TextChanged>>', self._mod)
        self.bind('<space>', self._space_pressed)
        self.bind('<Return>', self._return_pressed)
        self.bind('<Shift-Return>', self._shift_return_pressed)
        #self.bind('<Control-w>', self.select_word)
        self.bind('<Control-e>', self.insert_emphasis)

    def export(self, type, filename):
        text = self.get('1.0', 'end')
        self.exporter.export(text, type, filename)
        print('exported')
        
    def _key_pressed(self, event=None):
        if event.char in self.INLINECHARS:
            before = self.get(tk.INSERT + " -1c", tk.INSERT)
            after = self.get(tk.INSERT, tk.INSERT + " +1c")
            if before in self.WHITESPACE:
                if after in self.WHITESPACE:
                    if self.col_in_index(tk.INSERT) > 3:
                        self.insert(tk.INSERT, event.char*2)
                        self.mark_set(tk.INSERT, tk.INSERT + " -1c")
                        return "break"
                    #if this is the case we may be in a list. insert and wait for space pressed
                    else:
                        self.insert(tk.INSERT, event.char)
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
        #print(self.tag_names(self.index(tk.INSERT)))
        print(f"Position in Treesitter: {self.parser.find_position(self.index(tk.INSERT))}")
        print(f"Tag in text widget: {self.tag_names(self.index(tk.INSERT))}")

    def highlight(self, event=None):
        self.highlighter.highlight()
        return "break"

    def re_parse(self):
        self.parser.re_parse(self.get('1.0', 'end'))
        self.event_generate("<<PPEditorReparsed>>")

    def _full_parse(self):
        self.parser.parse(self.get('1.0', 'end'))
        self.event_generate("<<PPEditorReparsed>>")

    def _space_pressed(self, event=None):
        #delete selection, if present
        first, last = self.get_selection_indices()
        if first and last:
            self.delete(first, last)
            self.mark_set("insert", first)

        #if space is pressed after a list char and there are max 3 chars before the char we are in a list
        l_char = self.get(tk.INSERT + " -1c", tk.INSERT)
        if l_char in self.LISTCHARS:
            col = self.col_in_index(tk.INSERT + " -1c")
            if col <= 3:
               i = self.get_line_indent(tk.INSERT)
               if i == col:
                    print("listchar")
                    self.delete(tk.INSERT + " linestart", tk.INSERT)
                    self.insert(tk.INSERT + " linestart", l_char)

        #insert space
        self.insert(tk.INSERT, " ")
        #re-parse the document
        self.re_parse()
        return "break"


    def _return_pressed(self, event=None):
        #delete selection, if present
        first, last = self.get_selection_indices()
        if first and last:
            self.delete(first, last)
            self.mark_set("insert", first)

        #todo see whether we need to reparse here


        #if we just inserted an auto inserted text and Return is pressed immediately afterwards, delete the text again
        if 'auto_inserted_code_block' in self.tag_names(tk.INSERT + "-1c"):
            print("empty")
            if self.is_line_empty(tk.INSERT):
                self.tag_remove('auto_inserted_code_block', tk.INSERT + " linestart - 1c", tk.INSERT + " lineend + 1c")
                self.delete(tk.INSERT + " linestart", tk.INSERT)
                self.insert(tk.INSERT, "\n")
                self.re_parse()
                return "break"
            else:
                self.tag_remove('auto_inserted_code_block', tk.INSERT + " -1 line linestart", tk.INSERT + " lineend")

        if 'auto_inserted_list_bullet' in self.tag_names(tk.INSERT + "-1c"):
            self.tag_remove('auto_inserted_list_bullet', tk.INSERT + " -1 line linestart", tk.INSERT + " lineend")
            self.delete(tk.INSERT + " linestart", tk.INSERT)
            self.tag_add("list_paragraph", tk.INSERT + " linestart -1c", tk.INSERT + " lineend")
            self.tag_add("auto_inserted_list_para", tk.INSERT + " linestart -1c", tk.INSERT + " lineend + 1c")
            self.re_parse()
            return "break"

        if 'auto_inserted_list_para' in self.tag_names(tk.INSERT + "-1c"):
            if self.is_line_empty(tk.INSERT):
                print("enpty")
                self.tag_remove('auto_inserted_list_para', tk.INSERT + " -1 line linestart", tk.INSERT + " lineend + 1c")
                self.tag_remove('list_paragraph', tk.INSERT + " -1 line linestart", tk.INSERT + " lineend + 1c")
                self.insert(tk.INSERT, "\n", "paragraph")
                self.re_parse()
                return "break"
            else:
                self.tag_remove('auto_inserted_list_para', tk.INSERT + " -1 line linestart", tk.INSERT + " lineend + 1c")
                #self.insert(tk.INSERT, "\n")
                #self.re_parse()
                #return "break"

        if 'auto_inserted_block_quote' in self.tag_names(tk.INSERT + "-1c"):
            self.delete(tk.INSERT + " linestart", tk.INSERT)
            self.tag_remove('auto_inserted_block_quote', tk.INSERT + " -1 line linestart", tk.INSERT + " lineend")
            self.insert(tk.INSERT, "\n", "paragraph")
            self.tag_remove('block_quote', tk.INSERT + " -1 line linestart", tk.INSERT + " lineend + 1c")
            self.re_parse()
            return "break"

        #if the line contains a list_paragraph, search for the previous list marker and insert it, mark it auto_inserted
        if self._is_index_in(self.index(tk.INSERT + " -1c"), "list_item"):
            i1, i2 = self.tag_prevrange('list_marker',tk.INSERT, '1.0')
            #print(f"List maker: {i1}, {i2}")
            list_char = self.get(i1, i2)
            #if numbered increase number
            if len(list_char)>1:
                m = re.search(r"\d+", list_char)
                if m:
                    l_int = int(m.group())
                    l_int +=1
                    list_char = f"{l_int}."
            self.insert(tk.INSERT, "\n")
            self.insert(tk.INSERT, f"{list_char} ", ("auto_inserted_list_bullet", "lonely_list_marker"))
            self.re_parse()
            return "break"

        #if the line contains a blockquote insert > in the next line
        if self._is_index_in(self.index(tk.INSERT + " -1c"), "block_quote"):
            self.insert(tk.INSERT, "\n")
            self.insert(tk.INSERT, "> ", ("auto_inserted_block_quote", "block_quote"))
            self.re_parse()
            return "break"

        #if we are in an indented code block, insert the indentation of the current line in the next line
        if self.get_line_indent(tk.INSERT) >= 4:
            no_of_indent_chars = self.get_line_indent(tk.INSERT)-1
            self.insert(tk.INSERT, "\n")
            self.insert(tk.INSERT, f"{' '*no_of_indent_chars} ")
            self.tag_add("auto_inserted_code_block", tk.INSERT + " linestart -1c", tk.INSERT + " lineend + 1c")
            self.re_parse()
            return "break"

        #default. insert two returns and reparse the document
        self.insert(tk.INSERT, "\n\n")
        self.re_parse()
        self.see(tk.INSERT)
        return "break"

    def _shift_return_pressed(self, event=None):
        self.insert(tk.INSERT, "\n")
        return "break"

    def _mod(self, event=None):

        if not self.parser.tree:
            self._full_parse()
            return

        if not self.mod_ignore:

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
        #self.tag_remove('highlight', 1.0, tk.END)
        #self.tag_add('highlight', span[0], span[1])
        self.see(span[0])

    def show_hand_cursor(self, event=None):
        self.config(cursor="hand2")

    def show_arrow_cursor(self, event=None):
        self.config(cursor="arrow")

    def _is_index_in(self, index, element):
        #index is a tk index
        #element is a string equivalent to ts node type
        lis = self.parser.find_position(index)
        item = next((x for x in lis if x[0] == element), None)
        return item

    def link_clicked(self, event=None):
        index = self.index(f"@{event.x}, {event.y}")
        item = self._is_index_in(index, "link_destination")
        if item:
            link_text = self.get(my_utils.convert_point_ts_to_tk(item[1]), my_utils.convert_point_ts_to_tk(item[2]))
            if '#' in link_text:
                #todo linking up inline links
                print(f"Inline link: {link_text}")
            else:
                webbrowser.open(link_text, new=2, autoraise=True)
