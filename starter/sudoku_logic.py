import copy
import random

SIZE = 9
EMPTY = 0


def deep_copy(board):
    return copy.deepcopy(board)


def create_empty_board():
    return [[EMPTY for _ in range(SIZE)] for _ in range(SIZE)]


def is_safe(board, row, col, num):
    # Check row and column
    for x in range(SIZE):
        if board[row][x] == num or board[x][col] == num:
            return False
    # Check 3x3 box
    start_row = row - row % 3
    start_col = col - col % 3
    for i in range(3):
        for j in range(3):
            if board[start_row + i][start_col + j] == num:
                return False
    return True


def has_conflict(board, row, col, num):
    if num == EMPTY:
        return False

    for x in range(SIZE):
        if x != col and board[row][x] == num:
            return True

    for y in range(SIZE):
        if y != row and board[y][col] == num:
            return True

    start_row = row - row % 3
    start_col = col - col % 3
    for i in range(3):
        for j in range(3):
            r = start_row + i
            c = start_col + j
            if (r != row or c != col) and board[r][c] == num:
                return True

    return False


def is_complete(board, solution):
    return all(
        board[row][col] == solution[row][col]
        for row in range(SIZE)
        for col in range(SIZE)
    )


def get_hint(board, puzzle, solution):
    for row in range(SIZE):
        for col in range(SIZE):
            if puzzle[row][col] == EMPTY and board[row][col] == EMPTY:
                return row, col, solution[row][col]
    return None


def _find_empty_cell(board):
    for row in range(SIZE):
        for col in range(SIZE):
            if board[row][col] == EMPTY:
                return row, col
    return None


def count_solutions(board, limit=2):
    working = deep_copy(board)
    solution_count = 0

    def backtrack():
        nonlocal solution_count
        empty_cell = _find_empty_cell(working)
        if empty_cell is None:
            solution_count += 1
            return solution_count >= limit

        row, col = empty_cell
        for num in range(1, SIZE + 1):
            if is_safe(working, row, col, num):
                working[row][col] = num
                if backtrack():
                    return True
                working[row][col] = EMPTY
        return False

    backtrack()
    return solution_count


def fill_board(board):
    for row in range(SIZE):
        for col in range(SIZE):
            if board[row][col] == EMPTY:
                possible = list(range(1, SIZE + 1))
                random.shuffle(possible)
                for candidate in possible:
                    if is_safe(board, row, col, candidate):
                        board[row][col] = candidate
                        if fill_board(board):
                            return True
                        board[row][col] = EMPTY
                return False
    return True


def remove_cells(board, clues):
    positions = [(row, col) for row in range(SIZE) for col in range(SIZE)]
    random.shuffle(positions)
    for row, col in positions:
        if sum(1 for r in board for cell in r if cell != EMPTY) <= clues:
            break
        if board[row][col] == EMPTY:
            continue
        previous = board[row][col]
        board[row][col] = EMPTY
        if count_solutions(board, limit=2) != 1:
            board[row][col] = previous


def generate_puzzle(clues=35):
    max_attempts = 500
    for _ in range(max_attempts):
        board = create_empty_board()
        fill_board(board)
        solution = deep_copy(board)
        puzzle = deep_copy(board)
        remove_cells(puzzle, clues)
        if sum(1 for row in puzzle for cell in row if cell != EMPTY) == clues and count_solutions(puzzle, limit=2) == 1:
            return puzzle, solution

    raise RuntimeError('Unable to generate a unique Sudoku puzzle.')
