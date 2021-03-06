from tree_sitter import *
from tkinter import font
from PPEditorStyle import *
import PPUtils



class PPHighlighter():
    def __init__(self, editor, queries):
        self.editor = editor

        self.query_strings = queries

        # Outline contains header info#
        # (heading level, start of heading text, end of heading text)
        self.outline = []

        self.lineend_set = {"heading_content_1", "heading_content_2", "heading_content_3", "thight_list",
                            "list_paragraph", "paragraph", "block_quote", "block_block_quote", "indented_code_block",
                            "fenced_code_block"}
        self.linestart_set = {"indented_code_block", "fenced_code_block", "block_block_quote", "heading_marker_1"}

        self.auto_tags_set = {'auto_inserted_list_bullet', 'auto_inserted_list_para', 'auto_inserted_code_block', 'auto_inserted_block_quote'}

    def highlight(self):
        self.outline.clear()

        lines_to_highlight = self.editor.parser.changed_lines

        # remove all tags either in total doc or in the lines to highlight
        if lines_to_highlight:
            lines_to_highlight = (lines_to_highlight[0], lines_to_highlight[1] + 1)
            sindex = PPUtils.convert_point_ts_to_tk((lines_to_highlight[0], 0))
            eindex = PPUtils.convert_point_ts_to_tk((lines_to_highlight[1], 0))
        else:
            sindex = "1.0"
            eindex = "end"
        for tag in self.editor.tag_names():
            if tag not in self.auto_tags_set:
                self.editor.tag_remove(tag, sindex, eindex)

        # there is a bug in the markdown parser, which means that paragraphs cannot be found via a query.
        # look for all paragraphs directly under the document and tag them
        cursor = self.editor.parser.tree.root_node.walk()
        if cursor.goto_first_child():
            if (cursor.node.type == "paragraph" and
                    lines_to_highlight and
                    cursor.node.start_point[0] >= lines_to_highlight[0] and
                    cursor.node.end_point[0] <= lines_to_highlight[1]
            ):
                start_position = PPUtils.convert_point_ts_to_tk(cursor.node.start_point)
                end_position = PPUtils.convert_point_ts_to_tk(cursor.node.end_point)
                self.editor.tag_add("paragraph", start_position, end_position)
                print(f"I just tagged: {start_position}, {end_position}")

            while cursor.goto_next_sibling():
                if (cursor.node.type == "paragraph" and
                        lines_to_highlight and
                        cursor.node.start_point[0] >= lines_to_highlight[0] and
                        cursor.node.end_point[0] <= lines_to_highlight[1]
                ):
                    start_position = PPUtils.convert_point_ts_to_tk(cursor.node.start_point)
                    end_position = PPUtils.convert_point_ts_to_tk(cursor.node.end_point) + " lineend"
                    self.editor.tag_add("paragraph", start_position, end_position)
                    print(f"I just tagged: paragraph, {start_position}, {end_position}")

        for query_string in self.query_strings:
            captures = self.editor.parser.query_tree(query_string)
            # print(captures)

            # heading level
            heading_level = 0

            for item in captures:
                if (lines_to_highlight) and \
                        ((item[0].start_point[0] < lines_to_highlight[0]) or
                         (item[0].end_point[0] > lines_to_highlight[1])):
                    #even if outside, still update the outline (quick fix)
                    #todo maybe do not clear and redo the whole outline, but replace only the one changed
                    tag_name=item[1]
                    if tag_name == "atx_heading_marker":
                        heading_level = item[0].end_point[1] - item[0].start_point[1]
                        tag_name = tag_name + "_" + str(heading_level)

                    if (tag_name == "heading_content") and (heading_level != 0):
                        self.outline.append((heading_level, item[0].start_point, item[0].end_point))
                        tag_name = tag_name + "_" + str(heading_level)
                        heading_level = 0
                    continue

                tag_name = item[1]

                if tag_name == "atx_heading_marker":
                    heading_level = item[0].end_point[1] - item[0].start_point[1]
                    tag_name = tag_name + "_" + str(heading_level)

                if (tag_name == "heading_content") and (heading_level != 0):
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
                # print(f"I just tagged: {tag_name}, {start_position}, {end_position}")

        self.editor.see(tk.INSERT)