from timeit import default_timer as timer
import tkinter as tk
import re

class Text_Line(tk.Canvas):
    def __init__(self, width, index, colour='black', *args, **kwargs):
        tk.Canvas.__init__(self, borderwidth=0, highlightthickness=0, width=width, *args, **kwargs)
        self.width = width
        self.index = index
        self.colour = colour
        self.create_line(0,10, width, 10, fill=self.colour)

    def change_width(self, width):
        self.configure(width=width)
        self.create_line(0,10,width,10, fill=self.colour)

class Enhanced_Text(tk.Text):
    '''A text widget that doesn't permit inserts and deletes in regions tagged with "readonly"'''
    def __init__(self, *args, **kwargs):
        tk.Text.__init__(self, *args, **kwargs)

        #this gets the tk name of the widget
        widget = str(self)

        WIDGET_PROXY = '''
                       if {{[llength [info commands widget_proxy]] == 0}} {{
                           # Tcl code to implement a text widget proxy that disallows
                           # insertions and deletions in regions marked with "readonly"
                           proc widget_proxy {{actual_widget args}} {{
                               set command [lindex $args 0]
                               set args [lrange $args 1 end]
                               if {{$command == "insert"}} {{
                                   set index [lindex $args 0]
                                   if [_is_readonly $actual_widget $index "$index+1c"] {{
                                       bell
                                       return ""
                                   }}
                                   event generate {w_} <<BeforeTextChange>>
                                   $actual_widget $command {{*}}$args
                                   event generate {w_} <<AfterTextChange>>
                               }} elseif {{$command == "delete"}} {{
                                   foreach {{index1 index2}} $args {{
                                       if {{[_is_readonly $actual_widget $index1 $index2]}} {{
                                           bell
                                           return ""
                                       }}
                                   }}
                                   event generate {w_} <<BeforeTextChange>>
                                   $actual_widget $command {{*}}$args
                                   event generate {w_} <<AfterTextChange>>
                               }} elseif {{$command == "mark"}} {{
                                   set arg1 [lindex $args 0]
                                   set arg2 [lindex $args 1]
                                   set arg3 [lindex $args 2]
                                   if {{$arg1 == "set" && $arg2 == "insert"}} {{
                                       if {{"fenced" in [$actual_widget tag names $arg3]}} {{
                                           event generate {w_} <<BeforeEnteringFenced>> -data $arg3
                                           event generate {w_} <<AfterEnteringFenced>>
                                       }} else {{
                                           $actual_widget $command {{*}}$args
                                       }}
                                   }} else {{
                                       $actual_widget $command {{*}}$args
                                   }} 
                               }} else {{
                                   $actual_widget $command {{*}}$args
                               }}
                           }}

                           proc _is_readonly {{widget index1 index2}} {{
                               # return true if any text in the range between
                               # index1 and index2 has the tag "readonly"
                               set result false
                               if {{$index2 eq ""}} {{set index2 "$index1+1c"}}
                               # see if "readonly" is applied to any character in the
                               # range. There's probably a more efficient way to do this, but
                               # this is Good Enough
                               for {{set index $index1}} \
                                   {{[$widget compare $index < $index2]}} \
                                   {{set index [$widget index "$index+1c"]}} {{
                                       if {{"readonly" in [$widget tag names $index]}} {{
                                           set result true
                                           break
                                       }}
                                   }}
                               return $result
                           }}

                           proc _find_range {{widget ind1}} {{
                               set result {{}}
                               set lis [$widget tag ranges "fenced"]
                               foreach {{start, end}} lis {{
                               #    if {{[$widget compare $start < $ind1]}} {{
                               #        bell
                               #        lappend result $start $end
                               #        break
                               #    }}
                                   lappend result $start $end
                               }} 
                               return $result
                           }}
                       }}
                       '''.format(w_=widget)

        # this code creates a proxy that will intercept
        # each actual insert and delete.
        self.tk.eval(WIDGET_PROXY)

        # this code replaces the low level tk widget
        # with the proxy
        self.tk.eval('''
            rename {widget} _{widget}
            interp alias {{}} ::{widget} {{}} widget_proxy _{widget}
        '''.format(widget=widget))

        # search settings
        self.tag_configure('find_match', background="yellow")
        self.find_match_index = None
        self.find_search_starting_index = 1.0

        #properties
        self.last_change_range = ["1.0",tk.END]
        self.selection_present=False
        self._indent_re = re.compile(r'[ \t]*')

        # list of inline windows
        self.inline_windows = []

        #bind the events
        self.bind_events()

    def bind_events(self):
        self.bind('<Control-a>', self.select_all)
        self.bind('<Control-c>', self.copy)
        self.bind('<Control-v>', self.paste)
        self.bind('<Control-x>', self.cut)
        self.bind('<Control-y>', self.redo)
        self.bind('<Control-z>', self.undo)
        self.bind("<<BeforeTextChange>>", self.before_change)
        self.bind("<<AfterTextChange>>", self.after_change)
        #self.bind("<<BeforeInsertMove>>", self.before_insert_move)


        cmd = self._register(self._entering_fenced_callback)
        self.tk.call("bind", str(self), "<<BeforeEnteringFenced>>", cmd + " %d")

    def _entering_fenced_callback(self, data):
        want_index = self.index(data)
        cur_index = self.index(tk.INSERT)

        l1 = cur_index.split(".")
        cur_line = int(l1[0])
        cur_col = l1[1]

        l2 = want_index.split(".")
        want_line = int(l2[0])
        want_col = l2[1]

        # check in which direction the insert moves and extend movement by fenced text
        if cur_line > want_line:
            # case up
            fenced_start, fenced_end = self.tag_prevrange("fenced", cur_index)
            fs = int(fenced_start.split('.')[0]) - 1
            aim = str(fs) + "." + cur_col
            self.mark_set(tk.INSERT, aim)
        elif cur_line < want_line:
            # case down
            fenced_start, fenced_end = self.tag_nextrange("fenced", cur_index)
            fs = int(fenced_start.split('.')[0]) + 1
            aim = str(fs) + "." + cur_col
            self.mark_set(tk.INSERT, aim)
        elif cur_line == want_line:
            if '-' in data:
                # case left
                fenced_start, fenced_end = self.tag_prevrange("fenced", cur_index)
                aim = fenced_start + " - 1 char"
                self.mark_set(tk.INSERT, aim)
            elif '+' in data:
                # case right
                fenced_start, fenced_end = self.tag_nextrange("fenced", cur_index)
                aim = fenced_end + " + 1 char"
                self.mark_set(tk.INSERT, aim)
        else:
            # something wrong set index to initial target
            self.mark_set((tk.INSERT, want_index))

        return ("break")

    def before_change(self, event=None):
        #if there is a selection we need to store its range.
        t_range = self.tag_ranges("sel")
        if t_range:
            #str() needs to be used to convert the return items from tag_ranges into string
            self.last_change_range = [str(tag_pos) for tag_pos in list(t_range)]
            self.selection_present=True
        else:
        #if there is no selection save the insert mark before the insert or delete event
            self.last_change_range[0] = self.index(tk.INSERT)
            self.selection_present=False

    def after_change(self, event=None):
        #if there was a selection use it. Otherwise store insert mark after insertion/deletion event
        if not self.selection_present:
            self.last_change_range[1] = self.index(tk.INSERT)
            #if the range is not ordered (e.g. delete pressed), order it to guarantee smallest index first
            if not self.range_ordered(self.last_change_range):
                self.last_change_range.reverse()

        self.event_generate("<<TextChanged>>")

    def visible_lines(self):
        #returns the lines visible in the text widget. returns (index of first visible position, index of last visible position)
        start = self.index("@0,0")
        print("@{},{}".format(self.winfo_height(), self.winfo_width()))
        end = self.index("@{},{}".format(self.winfo_height(), self.winfo_width()))
        return (start, end)


    def convert_index_to_canonical(self, index):
        # convert an index to the canonical position in the string, e.g. "0.5" = 5
        count = self.count("1.0", index, "chars")
        if count == None:
            return 0
        else:
            return count[0]

    def select_word(self, event=None):
        self.tag_add("sel", tk.INSERT + " wordstart", tk.INSERT + " wordend")
        return "break"

    def line_in_index(self, index):
        return int(float(index))

    def col_in_index(self, mark):
        index = self.index(mark)
        return int(index.split('.')[1])

    def get_selection_indices(self):
        try:
            first = self.index("sel.first")
            last = self.index("sel.last")
            return first, last
        except tk.TclError:
            return None, None


    def find(self, text_to_find):
        length = tk.IntVar()
        idx = self.search(text_to_find, self.find_search_starting_index, stopindex=tk.END, count=length)

        if idx:
            self.tag_remove('find_match', 1.0, tk.END)

            end = f'{idx}+{length.get()}c'
            self.tag_add('find_match', idx, end)
            self.see(idx)

            self.find_search_starting_index = end
            self.find_match_index = idx
        else:
            if self.find_match_index != 1.0:
                if msg.askyesno("No more results", "No further matches. Repeat from the beginning?"):
                    self.find_search_starting_index = 1.0
                    self.find_match_index = None
                    return self.find(text_to_find)
            else:
                msg.showinfo("No Matches", "No matching text found")

    def replace_text(self, target, replacement):
        if self.find_match_index:
            current_found_index_line = str(self.find_match_index).split('.')[0]

            end = f"{self.find_match_index}+{len(target)}c"
            self.replace(self.find_match_index, end, replacement)

            self.find_search_starting_index = current_found_index_line + '.0'

    def cancel_find(self):
        self.find_search_starting_index = 1.0
        self.find_match_index = None
        self.tag_remove('find_match', 1.0, tk.END)

    def cut(self, event=None):
        self.event_generate("<<Cut>>")

        return "break"

    def copy(self, event=None):
        self.event_generate("<<Copy>>")

        return "break"

    def paste(self, event=None):
        self.event_generate("<<Paste>>")

        return "break"

    def undo(self, event=None):
        self.event_generate("<<Undo>>")

        return "break"

    def redo(self, event=None):
        self.event_generate("<<Redo>>")

        return "break"

    def select_all(self, event=None):
        self.tag_add("sel", 1.0, tk.END)

        return "break"

    def display_file_contents(self, filepath):
        with open(filepath, 'r') as file:
            self.delete(1.0, tk.END)
            self.insert(1.0, file.read())

    def range_ordered(self, range):
        left = list(map(int, range[0].split('.')))
        right = list(map(int, range[1].split('.')))
        if left[0] > right[0]:
            return False
        if right[0] > left[0]:
            return True
        if left[1] > right[1]:
            return False
        return True

    def get_line_indent(self, mark):
        line = self.get(mark + " linestart", mark)
        match = self._indent_re.match(line)
        return match.end()

    def index_in_range(self, index, start, end):
        if self.compare(start, "<=", index) and self.compare(index, "<=", end):
            return True
        else:
            return False

