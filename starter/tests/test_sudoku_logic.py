import sudoku_logic


def test_create_empty_board_returns_9x9_zero_grid():
    board = sudoku_logic.create_empty_board()

    assert len(board) == sudoku_logic.SIZE
    assert all(len(row) == sudoku_logic.SIZE for row in board)
    assert all(cell == sudoku_logic.EMPTY for row in board for cell in row)


def test_is_safe_detects_row_column_and_box_conflicts():
    board = sudoku_logic.create_empty_board()
    board[0][0] = 5
    board[0][1] = 1
    board[1][0] = 5

    assert sudoku_logic.is_safe(board, 0, 2, 5) is False
    assert sudoku_logic.is_safe(board, 2, 0, 5) is False

    board = sudoku_logic.create_empty_board()
    board[0][0] = 1
    board[0][1] = 2
    board[1][0] = 3
    board[1][1] = 1

    assert sudoku_logic.is_safe(board, 0, 2, 1) is False
    assert sudoku_logic.is_safe(board, 2, 2, 1) is False


def test_has_conflict_detects_row_column_and_box_duplicates():
    board = sudoku_logic.create_empty_board()
    board[0][0] = 5
    board[0][1] = 1
    board[1][0] = 5

    assert sudoku_logic.has_conflict(board, 0, 2, 5) is True
    assert sudoku_logic.has_conflict(board, 2, 0, 5) is True
    assert sudoku_logic.has_conflict(board, 0, 2, 4) is False

    board = sudoku_logic.create_empty_board()
    board[0][0] = 1
    board[0][1] = 2
    board[1][0] = 3
    board[1][1] = 1

    assert sudoku_logic.has_conflict(board, 0, 2, 1) is True
    assert sudoku_logic.has_conflict(board, 2, 2, 1) is True
    assert sudoku_logic.has_conflict(board, 2, 2, 9) is False


def test_is_complete_requires_all_cells_to_match_solution():
    solution = [
        [5, 3, 4, 6, 7, 8, 9, 1, 2],
        [6, 7, 2, 1, 9, 5, 3, 4, 8],
        [1, 9, 8, 3, 4, 2, 5, 6, 7],
        [8, 5, 9, 7, 6, 1, 4, 2, 3],
        [4, 2, 6, 8, 5, 3, 7, 9, 1],
        [7, 1, 3, 9, 2, 4, 8, 5, 6],
        [9, 6, 1, 5, 3, 7, 2, 8, 4],
        [2, 8, 7, 4, 1, 9, 6, 3, 5],
        [3, 4, 5, 2, 8, 6, 1, 7, 9],
    ]
    incomplete = sudoku_logic.deep_copy(solution)
    incomplete[0][0] = sudoku_logic.EMPTY
    incorrect = sudoku_logic.deep_copy(solution)
    incorrect[0][0] = 9

    assert sudoku_logic.is_complete(solution, solution) is True
    assert sudoku_logic.is_complete(incomplete, solution) is False
    assert sudoku_logic.is_complete(incorrect, solution) is False


def test_get_hint_returns_one_empty_editable_cell_with_solution_value():
    solution = [
        [5, 3, 4, 6, 7, 8, 9, 1, 2],
        [6, 7, 2, 1, 9, 5, 3, 4, 8],
        [1, 9, 8, 3, 4, 2, 5, 6, 7],
        [8, 5, 9, 7, 6, 1, 4, 2, 3],
        [4, 2, 6, 8, 5, 3, 7, 9, 1],
        [7, 1, 3, 9, 2, 4, 8, 5, 6],
        [9, 6, 1, 5, 3, 7, 2, 8, 4],
        [2, 8, 7, 4, 1, 9, 6, 3, 5],
        [3, 4, 5, 2, 8, 6, 1, 7, 9],
    ]
    puzzle = sudoku_logic.deep_copy(solution)
    puzzle[0][0] = sudoku_logic.EMPTY
    puzzle[0][1] = sudoku_logic.EMPTY
    board = sudoku_logic.deep_copy(puzzle)
    board[0][1] = 9

    assert sudoku_logic.get_hint(board, puzzle, solution) == (0, 0, 5)


def test_get_hint_returns_none_when_no_editable_cells_are_empty():
    solution = [[1 for _ in range(sudoku_logic.SIZE)] for _ in range(sudoku_logic.SIZE)]

    assert sudoku_logic.get_hint(solution, solution, solution) is None


def test_generate_puzzle_returns_valid_9x9_board_and_solution():
    puzzle, solution = sudoku_logic.generate_puzzle(35)

    assert len(puzzle) == sudoku_logic.SIZE
    assert len(solution) == sudoku_logic.SIZE
    assert all(len(row) == sudoku_logic.SIZE for row in puzzle)
    assert all(len(row) == sudoku_logic.SIZE for row in solution)
    assert any(cell == sudoku_logic.EMPTY for row in puzzle for cell in row)
    assert sum(1 for row in puzzle for cell in row if cell == sudoku_logic.EMPTY) > 0
    assert sum(1 for row in solution for cell in row if cell == 0) == 0

    for row in range(sudoku_logic.SIZE):
        for col in range(sudoku_logic.SIZE):
            if puzzle[row][col] != sudoku_logic.EMPTY:
                assert puzzle[row][col] == solution[row][col]


def test_count_solutions_on_solved_board():
    solved_board = [
        [5, 3, 4, 6, 7, 8, 9, 1, 2],
        [6, 7, 2, 1, 9, 5, 3, 4, 8],
        [1, 9, 8, 3, 4, 2, 5, 6, 7],
        [8, 5, 9, 7, 6, 1, 4, 2, 3],
        [4, 2, 6, 8, 5, 3, 7, 9, 1],
        [7, 1, 3, 9, 2, 4, 8, 5, 6],
        [9, 6, 1, 5, 3, 7, 2, 8, 4],
        [2, 8, 7, 4, 1, 9, 6, 3, 5],
        [3, 4, 5, 2, 8, 6, 1, 7, 9],
    ]

    assert sudoku_logic.count_solutions(solved_board, limit=2) == 1


def test_count_solutions_on_empty_board():
    empty_board = [[0 for _ in range(sudoku_logic.SIZE)] for _ in range(sudoku_logic.SIZE)]

    assert sudoku_logic.count_solutions(empty_board, limit=2) > 1


def test_generate_puzzle_has_exactly_one_solution():
    for _ in range(5):
        puzzle, solution = sudoku_logic.generate_puzzle(35)

        assert len(puzzle) == sudoku_logic.SIZE
        assert len(solution) == sudoku_logic.SIZE
        assert all(len(row) == sudoku_logic.SIZE for row in puzzle)
        assert all(len(row) == sudoku_logic.SIZE for row in solution)
        assert sudoku_logic.count_solutions(puzzle, limit=2) == 1
        assert puzzle != solution
        assert any(cell == sudoku_logic.EMPTY for row in puzzle for cell in row)


def _clue_count(board):
    return sum(1 for row in board for cell in row if cell != sudoku_logic.EMPTY)


def test_each_difficulty_has_expected_clue_count():
    easy, _ = sudoku_logic.generate_puzzle(45)
    medium, _ = sudoku_logic.generate_puzzle(35)
    hard, _ = sudoku_logic.generate_puzzle(25)

    assert _clue_count(easy) == 45
    assert _clue_count(medium) == 35
    assert _clue_count(hard) == 25


def test_difficulty_levels_have_expected_relative_clue_counts():
    easy, _ = sudoku_logic.generate_puzzle(45)
    medium, _ = sudoku_logic.generate_puzzle(35)
    hard, _ = sudoku_logic.generate_puzzle(25)

    assert _clue_count(easy) > _clue_count(medium) > _clue_count(hard)


def test_generated_puzzles_remain_uniquely_solvable_for_each_difficulty():
    easy, _ = sudoku_logic.generate_puzzle(45)
    medium, _ = sudoku_logic.generate_puzzle(35)
    hard, _ = sudoku_logic.generate_puzzle(25)

    assert sudoku_logic.count_solutions(easy, limit=2) == 1
    assert sudoku_logic.count_solutions(medium, limit=2) == 1
    assert sudoku_logic.count_solutions(hard, limit=2) == 1


def test_generated_puzzle_prefills_match_the_solution():
    puzzle, solution = sudoku_logic.generate_puzzle(35)

    for row in range(sudoku_logic.SIZE):
        for col in range(sudoku_logic.SIZE):
            if puzzle[row][col] != sudoku_logic.EMPTY:
                assert puzzle[row][col] == solution[row][col]
