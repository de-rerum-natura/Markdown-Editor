import tkinter.ttk as ttk
from PPHighlighter import PPHighlighter
from PPEditor import PPEditor
import PPUtils

class PPOutlineBrowser(ttk.Treeview):
    def __init__(self, master, editor, **kwargs):
        super().__init__(master, **kwargs)

        self['columns'] = ("start_index", "end_index")
        self['displaycolumns'] = ""
        self.span = ["0.0", "end"]
        self.id_counter = 0

        self.bind('<Double-Button-1>', self.node_selected)

        self.editor = editor

    def node_id(self, node):
        return "{}.{}.{}".format(node.type, node.start_byte, node.end_byte)



    def open_children(self, parent):
        self.item(parent, open=True)
        for child in self.get_children(parent):
            self.open_children(child)

    def update_tree(self):
        #print("outlineupdate")
        self.delete(*self.get_children())
        #todo fill in the tree view with the list
        outline_list = self.editor.highlighter.outline
        if outline_list:
            for item in outline_list:
                #print(item)
                start_index = PPUtils.convert_point_ts_to_tk(item[1])
                end_index = PPUtils.convert_point_ts_to_tk(item[2])
                text = (item[0]*"  ") + self.editor.get(start_index, end_index)
                self.insert('', 'end', text = text, values=[start_index, end_index])
        self.focus()

    def node_selected(self, event):
        #todo
        node = self.focus()
        begin_pos = self.set(node, "start")
        end_pos = self.set(node, "end")
        self.span = [begin_pos, end_pos]
        print(self.span)
        self.event_generate("<<PPNodeChosen>>")