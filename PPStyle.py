import json
import tkinter as tk


class PPStyle():
    def __init__(self, path):
        with open(path, 'r') as f:
            file_content = json.load(f)
        #the first list is the tree sitter queries
        self.queries = file_content[0]
        #the second list is styles
        self.styles = file_content[1]
        #first item in the styles list is the standard style
        self.editor_style = self.styles.pop(0)[1]
        self.standard = self.styles.pop(0)[1]

    def apply_style_to(self, editor):
        editor.configure(self.editor_style)
        self.configure_tags(editor)

    def configure_tags(self, editor):
        for style in self.styles:
            #{**dict1, **dict2} mergers to dicts whereas in case of collision the item of dict2 are kept
            editor.tag_configure(style[0], style[1])


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
