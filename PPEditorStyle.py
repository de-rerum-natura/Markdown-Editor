import json
import tkinter as tk
from tkinter import font


QUERIES = [
  "(document (paragraph) @paragraph)",
  "(atx_heading (atx_heading_marker) @atx_heading_marker (*(text)) @heading_content)",
  "((thematic_break) @thematic_break)",
  "((tight_list) @tight_list)",
  "((loose_list) @loose_list)",
  "(tight_list (list_item (list_marker) @lonely_list_marker))",
  "(tight_list (list_item (list_marker) @list_marker (*(text)) @list_paragraph))",
  "(loose_list (list_item (list_marker) @list_marker (*(text)) @list_paragraph))",
  "(link (link_text (text) @link_text))",
  "(link (link_text (text) @link_text) (link_destination (text) @link_destination))",
  "(link (link_text (text) @link_text) (link_destination (text) @link_destination) (link_title (text)) @link_title)",
  "(uri_autolink (text) @link_destination)",
  "((strong_emphasis) @strong_emphasis)",
  "((block_quote) @block_quote)",
  "(block_quote (block_quote (*(text))) @block_block_quote)",
  "((emphasis) @emphasis)",
  "((code_span) @code_span)",
  "((indented_code_block) @indented_code_block)",
  "((fenced_code_block) @fenced_code_block)"
]
class PPEditorStyle():
    def __init__(self):
        #with open(path, 'r') as f:
        #    file_content = json.load(f)

        self.queries = QUERIES
        #editor styles
        self.PADDING = 100
        self.FONT_FAMILY = "Times New Roman"
        self.FONT_STANDARD_SIZE = 14
        self.FOREGROUND = 'gray36'
        self.BACKGROUND = 'white'
        self.WRAP = 'word'
        self.TAG_COLOUR = "blue"



    def apply_style_to(self, editor):
        editor.configure(padx = self.PADDING,
                         font = [self.FONT_FAMILY, self.FONT_STANDARD_SIZE],
                         foreground= self.FOREGROUND,
                         background= self.BACKGROUND,
                         wrap= self.WRAP)
        self.configure_tags(editor)

    def configure_tags(self, editor):
        #this is replaced by tags hard coding due to bindings
        #for style in self.styles:
            #{**dict1, **dict2} mergers to dicts whereas in case of collision the item of dict2 are kept
        #    editor.tag_configure(style[0], style[1])

        #find lmargin2 for list paras
        text_font = font.Font(family=self.FONT_FAMILY, size=self.FONT_STANDARD_SIZE)
        list_width = text_font.measure("* ")
        blockquote_width = text_font.measure("> ")
        m_dis = text_font.measure("m")


        #paragraph tag
        editor.tag_configure("paragraph",
                             font= [self.FONT_FAMILY, self.FONT_STANDARD_SIZE],
                             foreground= self.FOREGROUND)

        #emphasis tags
        editor.tag_configure("emphasis",
                             font= [self.FONT_FAMILY, self.FONT_STANDARD_SIZE, "italic"])
        editor.tag_configure("strong_emphasis",
                             font= [self.FONT_FAMILY, self.FONT_STANDARD_SIZE, "bold"])

        # heading tags
        editor.tag_configure("atx_heading_marker_1",
                             foreground= self.TAG_COLOUR,
                             spacing1=50,
                             spacing3=20
                             )
        editor.tag_configure("heading_content_1",
                             font= [self.FONT_FAMILY, "28", "bold"],
                             foreground= "black")

        editor.tag_configure("atx_heading_marker_2",
                             foreground=self.TAG_COLOUR,
                             spacing1=20,
                             spacing3=10)
        editor.tag_configure("heading_content_2",
                             font= [self.FONT_FAMILY, "20", "bold"],
                             foreground= "black")

        editor.tag_configure("atx_heading_marker_3",
                             foreground=self.TAG_COLOUR,
                             spacing1=20,
                             spacing3=10)
        editor.tag_configure("heading_content_3",
                             font= [self.FONT_FAMILY, "18", "bold"],
                             foreground= "black")

        editor.tag_configure("atx_heading_marker_4",
                             foreground=self.TAG_COLOUR,
                             spacing1=20,
                             spacing3=10)
        editor.tag_configure("heading_content_4",
                             font=[self.FONT_FAMILY, "16", "bold"],
                             foreground="black")

        editor.tag_configure("atx_heading_marker_5",
                             foreground=self.TAG_COLOUR)
        editor.tag_configure("heading_content_5",
                             font=[self.FONT_FAMILY, self.FONT_STANDARD_SIZE, "bold"],
                             foreground="black")

        editor.tag_configure("atx_heading_marker_6",
                             foreground=self.TAG_COLOUR)
        editor.tag_configure("heading_content_6",
                             font=[self.FONT_FAMILY, self.FONT_STANDARD_SIZE, "italic"],
                             foreground="black")

        #thematic break tag
        editor.tag_configure("thematic_break",
                             foreground= self.TAG_COLOUR)

        #Link tags
        editor.tag_configure("link_text",
                             foreground= self.TAG_COLOUR)
        editor.tag_configure("link_destination",
                             foreground= self.TAG_COLOUR,
                             underline = 1)
        editor.tag_bind("link_destination", "<Enter>", editor.show_hand_cursor)
        editor.tag_bind("link_destination", "<Leave>", editor.show_arrow_cursor)
        editor.tag_bind("link_destination", "<Button-1>", editor.link_clicked)
        editor.tag_configure("link_title",
                             foreground= "green")

        #list tags
        editor.tag_configure("tight_list",
                             lmargin1=50,
                             lmargin2=50)
        editor.tag_configure("loose_list",
                             lmargin1=50,
                             lmargin2=50)
        editor.tag_configure("lonely_list_marker",
                             foreground= "gray20",
                             lmargin1=50)
        editor.tag_configure("list_marker",
                             foreground= self.TAG_COLOUR,
                             lmargin1=50)
        editor.tag_configure("list_paragraph",
                             lmargin1=50 + list_width,
                             lmargin2= 50 + list_width)

        #block quote tags
        editor.tag_configure("block_quote",
                             lmargin1=50,
                             lmargin2=50 + blockquote_width)
        editor.tag_configure("block_block_quote",
                             foreground= "red",
                             lmargin1=100,
                             lmargin2=100)

        #code tags
        editor.tag_configure("code_span",
                             background= "gray95",
                             borderwidth= 1,
                             relief= "solid")
        editor.tag_configure("indented_code_block",
                             background= "ghost white",
                             borderwidth=1,
                             relief= "solid",
                             lmargin1=50,
                             lmargin2=50)
        editor.tag_configure("fenced_code_block",
                             background= "ghost white",
                             borderwidth=1,
                             relief="solid",
                             lmargin1=50,
                             lmargin2=50)

        #auto inserted text
        editor.tag_configure("auto_inserted_code_block",
                             background= "ghost white",
                             borderwidth=1,
                             relief= "solid",
                             lmargin1=50,
                             lmargin2=50)
        editor.tag_configure("auto_inserted_list",
                             foreground='gray20',
                             background='gray92')
        editor.tag_configure("auto_inserted_list_para",
                             lmargin1=50 + list_width,
                             lmargin2=50 + list_width)
        #elided text
        editor.tag_configure("elided", elide=True)