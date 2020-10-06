

from tree_sitter import *
from PPUtils import *
from collections import deque

class PPParser:
    def __init__(self):
        Language.build_library('ts/my-languages.so',
                               ['C:/Users/Programmieren/PycharmProjects/Editor/tree-sitter-markdown-master'])

        self.language = Language('ts/my-languages.so', 'markdown')

        self.parser = Parser()
        self.parser.set_language(self.language)

        self.tree = None

        self.changed_nodes = []

        self.num_nodes = 0
        self.highlight = False

        self.changed_lines = None


    def parse(self, parse_string):
        self.tree = self.parser.parse(bytes(parse_string, "utf8"))
        print('full parse')

    def edit_tree(self, start_byte, old_end_byte, new_end_byte, start_point, old_end_point, new_end_point):
        self.tree.edit(
            start_byte=start_byte,
            old_end_byte=old_end_byte,
            new_end_byte=new_end_byte,
            start_point=start_point,
            old_end_point=old_end_point,
            new_end_point=new_end_point,
        )
        self.changed_lines = self.get_changed_span()
        if not self.changed_lines:
            self.changed_lines = (start_point[0], new_end_point[0])
        print(f"Changed lines: {self.changed_lines}")

    def re_parse(self, parse_string):
        #print("re-parse")
        old_tree = self.tree
        self.tree = self.parser.parse(bytes(parse_string, "utf8"), old_tree)

    def query_tree(self, query_string):
        query = self.language.query(query_string)
        captures = query.captures(self.tree.root_node)
        #print(query_string, len(captures))
        return captures
        # returns list of tuples (Node, "@...")


    def get_changed_nodes(self, node):
        result=[]
        def f(node):
            if node.has_changes:
                result.append(node)
        self._walk_children(node,f)
        self.changed_nodes = result



    def get_changed_span(self):
        result=[]
        def f(node):
            if node.has_changes:
                if node.type != "document":
                    result.append(node)

        self._walk_children(self.tree.root_node, f)

        if len(result)>0:
            lines = []
            for item in result:
                lines.extend((item.start_point[0], item.end_point[0]))
            return (min(lines), max(lines))
        else:
            return None


    def count_subnodes(self, node):
        #print("count subnotes")
        def f(node):
            pass
        return len(self._walk_children(node,f))

    def find_position(self, index):
        position = convert_point_tk_to_ts(index)
        result=[]
        def f(node):
            if ts_point_in_range(node.start_point, node.end_point, position):
                #print(f"found in {cursor.node.type}, start: {cursor.node.start_point}, end: {cursor.node.end_point}, position: {position}")
                result.append((node.type, node.start_point, node.end_point))

        # returns a list of tuples (String: type, (int, int): start position, (int, int): end position
        self._walk_children(self.tree.root_node, f)
        return result

    def _walk_children(self, node, func):
        to_visit = deque([node])
        visited = []

        while to_visit:
            current = to_visit.popleft()
            if current in visited:
                continue
            visited.append(current)
            func(current)
            to_visit.extend(current.children)
        return visited

    def tree_iter(self):
        to_visit = deque([self.tree.root_node])
        visited = []

        while to_visit:
            current = to_visit.popleft()
            if current in visited:
                continue
            visited.append(current)
            yield current
            to_visit.extend(current.children)


