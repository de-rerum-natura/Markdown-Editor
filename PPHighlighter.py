
from tree_sitter import *
from tkinter import font
from PPStyle import *
import PPUtils

class PPHighlighter():
    def __init__(self, editor, queries):
        self.editor = editor

        self.query_strings = queries

        self.outline = []

        self.lineend_set = {"heading_content_1", "heading_content_2", "heading_content_3", "thight_list", "list_paragraph", "paragraph", "block_quote", "block_block_quote", "indented_code_block", "fenced_code_block" }
        self.linestart_set = {"indented_code_block", "fenced_code_block"}
    def highlight(self):
        #print("highlighting")
        self.outline.clear()

        #remove all tags
        for tag in self.editor.tag_names():
            self.editor.tag_remove(tag, "1.0", "end")

        # there is a bug in the markdown parser, which means that paragraphs cannot be found via a query.
        # look for all paragraphs directly under the document and tag them
        cursor = self.editor.parser.tree.root_node.walk()
        if cursor.goto_first_child():
            print(cursor.node.type)
            if cursor.node.type == "paragraph":
                start_position = PPUtils.convert_point_ts_to_tk(cursor.node.start_point)
                end_position = PPUtils.convert_point_ts_to_tk(cursor.node.end_point)
                self.editor.tag_add("paragraph", start_position, end_position)
                #print("{}: {}, {}".format(cursor.node.type, start_position, end_position))

            while cursor.goto_next_sibling():
                if cursor.node.type == "paragraph":
                    start_position = PPUtils.convert_point_ts_to_tk(cursor.node.start_point)
                    end_position = PPUtils.convert_point_ts_to_tk(cursor.node.end_point) + " lineend"
                    self.editor.tag_add("paragraph", start_position, end_position)
                    #print("{}: {}, {}".format(cursor.node.type, start_position, end_position))

        for query_string in self.query_strings:
            captures = self.editor.parser.query_tree(query_string)
            #print(captures)

            #heading level
            heading_level = 0

            for item in captures:
                tag_name = item[1]

                if tag_name == "atx_heading_marker":
                    heading_level = item[0].end_point[1] - item[0].start_point[1]

                if (tag_name =="heading_content") and (heading_level != 0):
                    self.outline.append((heading_level, item[0].start_point, item[0].end_point))
                    tag_name = tag_name + "_" + str(heading_level)
                    heading_level = 0

                start_position = PPUtils.convert_point_ts_to_tk(item[0].start_point)
                end_position = PPUtils.convert_point_ts_to_tk(item[0].end_point)
                if tag_name in self.lineend_set:
                    end_position = end_position + " lineend + 1c"
                if tag_name in self.linestart_set:
                    start_position = start_position + " linestart"

                self.editor.tag_add(tag_name, start_position, end_position)