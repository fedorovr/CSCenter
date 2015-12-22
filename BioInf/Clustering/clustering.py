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
                       ("K", "L"): 11, ("K", "M"): 11, ("K", "N"): 8,
                      }

distance_matrix_three = {("d", "e"): 3,
                         ("c", "d"): 8, ("c", "e"): 7,
                         ("b", "c"): 10, ("b", "d"): 10, ("b", "e"): 9,
                         ("a", "b"): 5, ("a", "c"): 9,  ("a", "d"): 9, ("a", "e"): 8
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
    for elem_one, elem_two in list(distance_matrix):
        distance_matrix[elem_two, elem_one] = distance_matrix[elem_one, elem_two]
        node_for_code[elem_one] = Node(None, None, 0, 0, 0, elem_one)
        node_for_code[elem_two] = Node(None, None, 0, 0, 0, elem_two)

    while distance_matrix:
        # Find 2 closest elements and merge them
        code_one, code_two = min(distance_matrix, key=distance_matrix.get)
        min_dist = distance_matrix[code_one, code_two]
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
                if other_node != code_two:
                    nodes_to_add[other_node, new_code] = \
                        (distance_matrix[other_node, code_one] + distance_matrix[other_node, code_two]) / 2
                    nodes_to_add[new_code, other_node] = \
                        (distance_matrix[other_node, code_one] + distance_matrix[other_node, code_two]) / 2

        # Delete distances to objects which we merged. list() for copy
        for k in list(distance_matrix):
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
    for elem_one, elem_two in list(distance_matrix):
        distance_matrix[elem_two, elem_one] = distance_matrix[elem_one, elem_two]
        node_for_code[elem_one] = Node(None, None, 0, 0, 0, elem_one)
        node_for_code[elem_two] = Node(None, None, 0, 0, 0, elem_two)

    while distance_matrix:
        # Find 2 closest elements and merge them
        code_one, code_two = min(distance_matrix, key=distance_matrix.get)
        min_dist = distance_matrix[code_one, code_two]
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
                if other_node != code_two:
                    nodes_to_add[other_node, new_code] = \
                        (distance_matrix[other_node, code_one] * len(code_one) +
                         distance_matrix[other_node, code_two] * len(code_two)) / (len(code_one) + len(code_two))
                    nodes_to_add[new_code, other_node] = \
                        (distance_matrix[other_node, code_one] * len(code_one) +
                         distance_matrix[other_node, code_two] * len(code_two)) / (len(code_one) + len(code_two))

        # Delete distances to objects which we merged. list() for copy
        for k in list(distance_matrix):
            if code_one in k or code_two in k:
                del distance_matrix[k]

        for k in nodes_to_add:
            distance_matrix[k] = nodes_to_add[k]

    print(node_for_code[max(node_for_code, key=len)].to_string())

    # Optional code for displaying tree with Biopy and matplotlib
    tree = Phylo.read(StringIO(node_for_code[max(node_for_code, key=len)].to_string()), "newick")
    tree.ladderize()   # Flip branches so deeper clades are displayed at top
    Phylo.draw(tree)


def neighbour_joining(dist_matrix):
    # Make our own copy
    distance_matrix = dict(dist_matrix)
    for elem_one, elem_two in list(distance_matrix):
        distance_matrix[elem_two, elem_one] = distance_matrix[elem_one, elem_two]

    node_for_code = {}
    # create set with all nodes
    taxa = set()
    for p1, p2 in distance_matrix:
        taxa.add(p1)
        taxa.add(p2)

    for taxon in taxa:
        node_for_code[taxon] = Node(None, None, 0, 0, 0, taxon)
        distance_matrix[taxon, taxon] = 0

    while len(taxa) > 2:
        n = len(taxa)
        q_matrix = {}
        for taxon_one in taxa:
            for taxon_two in taxa:
                if taxon_one != taxon_two:
                    q_matrix[taxon_one, taxon_two] = (n - 2) * distance_matrix[taxon_one, taxon_two] - \
                                                     sum(distance_matrix[taxon_one, k] for k in taxa) - \
                                                     sum(distance_matrix[taxon_two, k] for k in taxa)

        # Extract min and create new node
        code_one, code_two = min(q_matrix, key=q_matrix.get)
        code_one_dist = 0.5 * distance_matrix[code_one, code_two] + 1.0 / (2 * (n - 2)) * \
                        (sum(distance_matrix[code_one, k] for k in taxa) - sum(distance_matrix[code_two, k] for k in taxa))
        code_two_dist = distance_matrix[code_one, code_two] - code_one_dist
        new_code = code_one + code_two

        n_one = node_for_code[code_one]
        n_two = node_for_code[code_two]

        node_for_code[new_code] = Node(n_one, n_two, code_one_dist, code_two_dist, 0, new_code)

        # Recalculate distances between other taxa and new one
        taxa.discard(code_one)
        taxa.discard(code_two)
        for taxon in taxa:
            distance_matrix[taxon, new_code] = 0.5 * (distance_matrix[code_one, taxon] +
                                                      distance_matrix[code_two, taxon] -
                                                      distance_matrix[code_one, code_two])
            distance_matrix[new_code, taxon] = distance_matrix[taxon, new_code]
        taxa.add(new_code)
        distance_matrix[new_code, new_code] = 0

        # Delete distances to objects which we merged. list() for copy
        for k in list(distance_matrix):
            if code_one in k or code_two in k:
                del distance_matrix[k]

    # At this point we have 2 big taxa, so merge them and get a final result
    taxon_one, taxon_two = taxa
    new_code = taxon_one + taxon_two
    node_for_code[new_code] = Node(node_for_code[taxon_one], node_for_code[taxon_two],
                                   distance_matrix[taxon_one, taxon_two], 0, 0, new_code)

    print(node_for_code[max(node_for_code, key=len)].to_string())

    # Optional code for displaying tree with Biopy and matplotlib
    tree = Phylo.read(StringIO(node_for_code[max(node_for_code, key=len)].to_string()), "newick")
    tree.ladderize()   # Flip branches so deeper clades are displayed at top
    Phylo.draw(tree)


wpgma(distance_matrix_two)
upgma(distance_matrix_two)
neighbour_joining(distance_matrix_one)
