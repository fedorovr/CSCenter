from Bio import Phylo
from io import StringIO

distance_matrix_one = {("B", "A"): 5,
                       ("C", "A"): 4, ("C", "B"): 7,
                       ("D", "A"): 7, ("D", "B"): 10, ("D", "C"): 7,
                       ("E", "A"): 6, ("E", "B"): 9,  ("E", "C"): 6, ("E", "D"): 5,
                       ("F", "A"): 8, ("F", "B"): 11, ("F", "C"): 8, ("F", "D"): 9, ("F", "E"): 8,
                      }

distance_matrix_two = {("M", "N"): 4,
                       ("L", "M"): 8, ("L", "N"): 8,
                       ("K", "L"): 16, ("K", "M"): 16, ("K", "N"): 10,
                      }


class Node:
    def __init__(self, left, right, dist_left, dist_right, overall_dist, value):
        self.left = left
        self.right = right
        self.distance_left = dist_left
        self.distance_right = dist_right
        self.overall_dist = overall_dist
        self.value = value

    def to_string(self):
        if self.left is None and self.right is None:
            return self.value
        else:
            return "(" + self.left.to_string() + "):" + str(self.distance_left) +\
                ", (" + self.right.to_string() + "):" + str(self.distance_right)


def wpgma(dist_matrix):
    """Weighted Pair Group Method with Arithmetic Mean"""

    node_for_code = {}
    # Make our own copy
    distance_matrix = dict(dist_matrix)
    for elem_one, elem_two in list(distance_matrix.keys()):
        distance_matrix[elem_two, elem_one] = distance_matrix[elem_one, elem_two]
        node_for_code[elem_one] = Node(None, None, 0, 0, 0, elem_one)
        node_for_code[elem_two] = Node(None, None, 0, 0, 0, elem_two)

    while len(distance_matrix):
        # Find 2 closest elements and merge them
        code_one, code_two = (min(distance_matrix, key=distance_matrix.get))
        min_dist = distance_matrix[(code_one, code_two)]
        new_code = code_one + code_two
        nodes_to_add = {}

        n_one = node_for_code[code_one]
        n_two = node_for_code[code_two]

        node_for_code[new_code] = Node(n_one, n_two,
                                       min_dist / 2 - n_one.overall_dist, min_dist / 2 - n_two.overall_dist,
                                       min_dist / 2, new_code)

        # Recalculate distance to new element
        for k in distance_matrix:
            if code_one in k:
                other_node = k[1] if k[0] == code_one else k[0]
                if other_node == code_two:
                    continue
                nodes_to_add[(other_node, new_code)] = \
                    (distance_matrix[(other_node, code_one)] + distance_matrix[(other_node, code_two)]) / 2
                nodes_to_add[(new_code, other_node)] = \
                    (distance_matrix[(other_node, code_one)] + distance_matrix[(other_node, code_two)]) / 2

        # Delete distances to objects, which we merged
        for k in list(distance_matrix.keys()):
            if code_one in k or code_two in k:
                del distance_matrix[k]

        for k in nodes_to_add:
            distance_matrix[k] = nodes_to_add[k]

    print(node_for_code[max(node_for_code, key=len)].to_string())

    # Optional code for displaying tree with Biopy and matplotlib
    tree = Phylo.read(StringIO(node_for_code[max(node_for_code, key=len)].to_string()), "newick")
    tree.ladderize()   # Flip branches so deeper clades are displayed at top
    Phylo.draw(tree)


def upgma(dist_matrix):
    """Unweighted Pair Group Method with Arithmetic Mean"""

    node_for_code = {}
    # Make our own copy
    distance_matrix = dict(dist_matrix)
    for elem_one, elem_two in list(distance_matrix.keys()):
        distance_matrix[elem_two, elem_one] = distance_matrix[elem_one, elem_two]
        node_for_code[elem_one] = Node(None, None, 0, 0, 0, elem_one)
        node_for_code[elem_two] = Node(None, None, 0, 0, 0, elem_two)

    while len(distance_matrix):
        # Find 2 closest elements and merge them
        code_one, code_two = (min(distance_matrix, key=distance_matrix.get))
        min_dist = distance_matrix[(code_one, code_two)]
        new_code = code_one + code_two
        nodes_to_add = {}

        n_one = node_for_code[code_one]
        n_two = node_for_code[code_two]

        node_for_code[new_code] = Node(n_one, n_two,
                                       min_dist / 2 - n_one.overall_dist, min_dist / 2 - n_two.overall_dist,
                                       min_dist / 2, new_code)

        # Recalculate distance to new element
        for k in distance_matrix:
            if code_one in k:
                other_node = k[1] if k[0] == code_one else k[0]
                if other_node == code_two:
                    continue
                nodes_to_add[(other_node, new_code)] = \
                    (distance_matrix[(other_node, code_one)] * len(code_one) +
                     distance_matrix[(other_node, code_two)] * len(code_two)) / (len(code_one) + len(code_two))
                nodes_to_add[(new_code, other_node)] = \
                    (distance_matrix[(other_node, code_one)] * len(code_one) +
                     distance_matrix[(other_node, code_two)] * len(code_two)) / (len(code_one) + len(code_two))

        # Delete distances to objects, which we merged
        for k in list(distance_matrix.keys()):
            if code_one in k or code_two in k:
                del distance_matrix[k]

        for k in nodes_to_add:
            distance_matrix[k] = nodes_to_add[k]

    print(node_for_code[max(node_for_code, key=len)].to_string())

    # Optional code for displaying tree with Biopy and matplotlib
    tree = Phylo.read(StringIO(node_for_code[max(node_for_code, key=len)].to_string()), "newick")
    tree.ladderize()   # Flip branches so deeper clades are displayed at top
    Phylo.draw(tree)


wpgma(distance_matrix_one)
upgma(distance_matrix_one)
