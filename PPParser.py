

from tree_sitter import *

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

    def re_parse(self, parse_string):
        print("re-parse")
        old_tree = self.tree
        self.tree = self.parser.parse(bytes(parse_string, "utf8"), old_tree)


    def query_tree(self, query_string):
        query = self.language.query(query_string)
        captures = query.captures(self.tree.root_node)
        #print(query_string, len(captures))
        return captures
        # returns list of tuples (Node, "@...")

    def recursiveTreeWalk(self, node):
        res = []
        if node.has_changes:
            res.append(node)
        if len(node.children) > 0:
            for child in node.children:
                res = res + self.recursiveTreeWalk(child)
        return res

    def get_changed_nodes(self, node):
        self.changed_nodes = self.recursiveTreeWalk(node)

    def get_changed_span(self, node):
        result = self.get_changed_nodes(node)
        start_points = []
        end_points = []
        for item in results:
            start_points.append(item.start_point)
            end_points.append(item.end_point)


    def recursive_tree_walk_cursor(self, node):
        i=0
        cursor = node.walk()
        i =+1
        if cursor.goto_first_child():
           i = i + self.recursive_tree_walk_cursor(cursor.node)
           while cursor.goto_next_sibling():
               i = i + self.recursive_tree_walk_cursor(cursor.node)
        return i

    def count_subnodes(self, node):
        #print("count subnotes")
        return self.recursive_tree_walk_cursor(node)