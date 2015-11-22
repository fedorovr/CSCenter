sigma = -3.4
mu = -7
eq = 1
p = -1
penalties = {("A", "A"): 5, ("A", "K"): -1, ("A", "N"): -1, ("A", "R"): -2, ("K", "K"): 6,
             ("K", "N"): 0, ("K", "R"): -7,  ("N", "N"): 7,  ("N", "R"): -1, ("R", "R"): 7}


def get_penalty2(char_one, char_two):
    if char_one > char_two:
        char_one, char_two = char_two, char_one
    return penalties[char_one, char_two]


def get_penalty1(char_one, char_two):
    return mu if char_one != char_two else eq


def show_matrix(m):
    for r in range(len(m)):
        for c in range(len(m[0])):
            print(("{:6.2f}".format(m[r][c])), end="")
        print()


def get_optimal_alignment(first_seq, second_seq, matrix, get_penalty):
    rows, cols = len(matrix), len(matrix[0])
    cur_row, cur_col = rows - 1, cols - 1
    alignment_one, alignment_two = [], []
    while (cur_row, cur_col) != (0, 0):
        if cur_row-1 and cur_col-1:
            left_upper_val = matrix[cur_row-1][cur_col-1] + get_penalty(first_seq[cur_row], second_seq[cur_col])
        else:
            left_upper_val = -float("inf") 
        left_val = matrix[cur_row][cur_col-1] + sigma if cur_col-1 else -float("inf")
        upper_val = matrix[cur_row-1][cur_col] + sigma if cur_row-1 else -float("inf")
        if left_upper_val >= left_val and left_upper_val >= upper_val:
            alignment_one.append(first_seq[cur_row])
            alignment_two.append(second_seq[cur_col])
            cur_row, cur_col = cur_row - 1, cur_col - 1
        elif upper_val >= left_upper_val and upper_val >= left_val:
            alignment_one.append(first_seq[cur_row])
            alignment_two.append("-")
            cur_row -= 1
        else:       # left_val is the biggest
            alignment_one.append("-")
            alignment_two.append(second_seq[cur_col])
            cur_col -= 1
    return "\n".join(("".join(reversed(alignment_one)), "".join(reversed(alignment_two))))


def get_optimal_local_alignment(first_seq, second_seq, matrix, get_penalty, max_row, max_col):
    cur_row, cur_col = max_row, max_col
    alignment_one, alignment_two = [], []
    while matrix[cur_row][cur_col] > 0:
        if cur_row and cur_col:
            left_upper_val = matrix[cur_row-1][cur_col-1] + get_penalty(first_seq[cur_row], second_seq[cur_col])
        else:
            left_upper_val = -float("inf") 
        left_val = matrix[cur_row][cur_col-1] + sigma if cur_col else -float("inf")
        upper_val = matrix[cur_row-1][cur_col] + sigma if cur_row else -float("inf")
        if left_upper_val >= left_val and left_upper_val >= upper_val:
            alignment_one.append(first_seq[cur_row])
            alignment_two.append(first_seq[cur_row])
            cur_row, cur_col = cur_row - 1, cur_col - 1
        elif upper_val >= left_upper_val and upper_val >= left_val:
            alignment_one.append(first_seq[cur_row])
            alignment_two.append("-")
            cur_row -= 1
        else:        # left_val is the biggest
            alignment_one.append("-")
            alignment_two.append(second_seq[cur_col])
            cur_col -= 1
    return "\n".join(("".join(reversed(alignment_one)), "".join(reversed(alignment_two))))


def build_matrix(filename):
    with open(filename) as f:
        lines = f.readlines()
    if len(lines) != 4 or not (lines[0].startswith(">") and lines[2].startswith(">") and
                               lines[1].endswith("*\n") and lines[3].endswith("*")):
        print("Incorrect Input")
        return
    first_seq, second_seq = "$" + (lines[1])[:-2], "$" + (lines[3])[:-1]
    matrix = [[0 for _ in range(len(second_seq))] for _ in range(len(first_seq))]
    for r in range(len(first_seq)):
        matrix[r][0] = sigma * r
    for c in range(len(second_seq)):
        matrix[0][c] = sigma * c
    return matrix, first_seq, second_seq


def build_optimal_alignment(filename, get_penalty, please_display_matrix=False):
    matrix, first_seq, second_seq = build_matrix(filename)
    for r in range(1, len(first_seq)):
        for c in range(1, len(second_seq)):
            matrix[r][c] = max(matrix[r-1][c-1] + get_penalty(first_seq[r], second_seq[c]),
                               matrix[r-1][c] + sigma,
                               matrix[r][c-1] + sigma)
    if please_display_matrix:
        show_matrix(matrix)	
    print(get_optimal_alignment(first_seq, second_seq, matrix, get_penalty))


def build_optimal_local_alignment(filename, get_penalty, please_display_matrix=False):
    """Smith-Waterman algorithm"""
    matrix, first_seq, second_seq = build_matrix(filename)
    max_value, max_row, max_col = -float("inf"), 0, 0
    for r in range(1, len(first_seq)):
        for c in range(1, len(second_seq)):
            matrix[r][c] = max(matrix[r-1][c-1] + get_penalty(first_seq[r], second_seq[c]),
                               matrix[r-1][c] + sigma,
                               matrix[r][c-1] + sigma,
                               0)
            if matrix[r][c] > max_value:
                max_value, max_row, max_col = matrix[r][c], r, c	
    if please_display_matrix:
        show_matrix(matrix)
    print(get_optimal_local_alignment(first_seq, second_seq, matrix, get_penalty, max_row, max_col))


build_optimal_alignment("input.txt", get_penalty1)
build_optimal_alignment("input2.txt", get_penalty2)
build_optimal_local_alignment("input3.txt", get_penalty1, please_display_matrix=True)
