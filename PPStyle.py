import json
import tkinter as tk
from tkinter import font


class PPStyle():
    def __init__(self, path):
        with open(path, 'r') as f:
            file_content = json.load(f)
        #the first list is the tree sitter queries
        self.queries = file_content[0]
        #the second list is styles - this is replaced with hardcoding due to bindings
        #self.styles = file_content[1]
        #first item in the styles list is the standard style
        #self.editor_style = self.styles.pop(0)[1]
        #self.standard = self.styles.pop(0)[1]


    def apply_style_to(self, editor):
        editor.configure(padx = 100, font = ["Times New Roman", "14"], foreground= "gray36", background= "white", borderwidth= 0, relief=  "flat")
        self.configure_tags(editor)

    def configure_tags(self, editor):
        #this is replaced by tags hard coding due to bindings
        #for style in self.styles:
            #{**dict1, **dict2} mergers to dicts whereas in case of collision the item of dict2 are kept
        #    editor.tag_configure(style[0], style[1])

        #find lmargin2 for list paras
        text_font = font.Font(family="Times New Roman", size=14)
        list_width = text_font.measure("* ")
        m_dis = text_font.measure("m")


        #paragraph tag
        editor.tag_configure("paragraph", font= ["Times New Roman", "14"], foreground= "gray36")

        #emphasis tags
        editor.tag_configure("emphasis", font= ["Times New Roman", "14", "italic"])
        editor.tag_configure("strong_emphasis", font= ["Times New Roman", "14", "bold"])

        # heading tags
        editor.tag_configure("atx_heading_marker", foreground= "blue")
        editor.tag_configure("heading_content_1", font= ["Times New Roman", "28", "bold"], foreground= "black")
        editor.tag_configure("heading_content_2", font= ["Times New Roman", "20", "bold"], foreground= "black")
        editor.tag_configure("heading_content_3", font= ["Times New Roman", "18", "bold"], foreground= "black")
        editor.tag_configure("heading_content_4", font=["Times New Roman", "16", "bold"], foreground="black")
        editor.tag_configure("heading_content_5", font=["Times New Roman", "14", "bold"], foreground="black")
        editor.tag_configure("heading_content_6", font=["Times New Roman", "14", "italic"], foreground="black")

        #thematic break tag
        editor.tag_configure("thematic_break", foreground= "blue")

        #Link tags
        editor.tag_configure("link_text", foreground= "blue")
        editor.tag_configure("link_destination", foreground= "blue", underline = 1)
        editor.tag_bind("link_destination", "<Enter>", editor.show_hand_cursor)
        editor.tag_bind("link_destination", "<Leave>", editor.show_arrow_cursor)
        editor.tag_bind("link_destination", "<Button-1>", editor.link_clicked)
        editor.tag_configure("link_title", foreground= "green")

        #list tags
        editor.tag_configure("tight_list", lmargin1=50, lmargin2=50)
        editor.tag_configure("loose_list", lmargin1=50, lmargin2=50)
        editor.tag_configure("lonely_list_marker", foreground= "gray20", lmargin1=50)
        editor.tag_configure("list_marker", foreground= "blue", lmargin1=50)
        editor.tag_configure("list_paragraph", lmargin1=50 + list_width, lmargin2= 50 + list_width)

        #block quote tags
        editor.tag_configure("block_quote", lmargin1=50, lmargin2=50)
        editor.tag_configure("block_block_quote", foreground= "red", lmargin1=70, lmargin2=70)

        #code tags
        editor.tag_configure("code_span", background= "gray95", borderwidth= 1, relief= "solid")
        editor.tag_configure("indented_code_block", background= "ghost white", borderwidth=1, relief= "solid", lmargin1=50, lmargin2=50)
        editor.tag_configure("fenced_code_block", background= "ghost white", borderwidth=1, relief="solid", lmargin1=50, lmargin2=50)

        #auto inserted text
        editor.tag_configure("auto_inserted_code_block", foreground='gray20', background = 'gray92')
        editor.tag_configure("auto_inserted_list", foreground='gray20', background='gray92')


#this is for testing only
if __name__ == "__main__":
    p = PPStyle("C:/Users/Programmieren/PycharmProjects/Editor/style.json")
    for query in p.queries:
        print("Query: {}".format(query))

    print("Standard: {}".format(p.standard))

    for style in p.styles:
        print(style)

    editor = tk.Text()
    for style in p.styles:
        editor.tag_configure(style[0], style[1])
