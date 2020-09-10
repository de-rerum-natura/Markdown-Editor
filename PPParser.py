

from tree_sitter import *
from PPUtils import *

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

    def _recursive_get_changed_nodes(self, node):
        res = []
        if node.has_changes:
            res.append(node)
        if len(node.children) > 0:
            for child in node.children:
                res = res + self._recursive_get_changed_nodes(child)
        return res

    def get_changed_nodes(self, node):
        self.changed_nodes = self._recursive_get_changed_nodes(node)


    def _recursive_get_changed_span(self, func, node):
        result = []
        cursor = node.walk()
        if cursor.goto_first_child():
            func(cursor.node, result)
        while cursor.goto_next_sibling():
            func(cursor.node, result)
        return result

    def get_changed_span(self):
        def func(node, result):
            if node.has_changes:
                if node.type != "document":
                    result.append(node)
                result = result + self._recursive_get_changed_span(func, node)

        result = self._recursive_get_changed_span(func, self.tree.root_node)

        if result:
            lines = []
            for item in result:
                lines.extend((item.start_point[0], item.end_point[0]))
            return (min(lines), max(lines))
        else:
            return None


    def _recursive_count_subnodes(self, node):
        i=0
        cursor = node.walk()
        i =+1
        if cursor.goto_first_child():
           i = i + self._recursive_count_subnodes(cursor.node)
           while cursor.goto_next_sibling():
               i = i + self._recursive_count_subnodes(cursor.node)
        return i

    def count_subnodes(self, node):
        #print("count subnotes")
        return self._recursive_count_subnodes(node)

    def _recursive_find_position(self, node, position):
        result = []
        cursor = node.walk()
        if cursor.goto_first_child():
            if ts_point_in_range(cursor.node.start_point, cursor.node.end_point, position):
                #print(f"found in {cursor.node.type}, start: {cursor.node.start_point}, end: {cursor.node.end_point}, position: {position}")
                result.append((cursor.node.type, cursor.node.start_point, cursor.node.end_point))
                result = result + self._recursive_find_position(cursor.node, position)
        while cursor.goto_next_sibling():
            if ts_point_in_range(cursor.node.start_point, cursor.node.end_point, position):
                #print(f"found in {cursor.node.type}, start: {cursor.node.start_point}, end: {cursor.node.end_point}, position: {position}")
                result.append((cursor.node.type, cursor.node.start_point, cursor.node.end_point))
                result = result + self._recursive_find_position(cursor.node, position)
        return result

    def find_position(self, index):
        position = convert_point_tk_to_ts(index)
        # returns a list of tuples (String: type, (int, int): start position, (int, int): end position
        return self._recursive_find_position(self.tree.root_node, position)


