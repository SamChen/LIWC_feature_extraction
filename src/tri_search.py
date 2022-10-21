#!/usr/bin/env python


class Node():
    def __init__(self, char):
        self.children : Dict[str, Node] = {}  # mapping from character ==> Node
        self.value = None
        self.char = char

def find(node: Node, key: list):

    # end point for fix words
    if len(key) == 0 and "*" not in node.children:
        return node.value

    # end point for wild words
    if node.char == "*":
        return node.value


    # if regular node exist
    if len(key) > 0 and key[0] in node.children:
        char, *key = key
        regular_node = node.children[char]
        # print("regular: {}".format(key))
        result = find(regular_node, key)
        if result:
            return result

    # if wild node exist
    if "*" in node.children:
        wild_node = node.children["*"]
        # print("wild: {}".format(key))
        result = find(wild_node, key)
        if result:
            return result

    return None




def insert(node: Node, key: str, value: str) -> None:
    # end situation
    if len(key) == 0:
        node.value = value
        return

    else:
        char, *key = key
        if char not in node.children:
            node.children[char] = Node(char)
        node = node.children[char]
        return insert(node, key, value)

