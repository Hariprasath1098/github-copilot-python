import app as app_module


app_module.app.config['TESTING'] = True


def test_index_route_returns_page():
    client = app_module.app.test_client()
    response = client.get('/')

    assert response.status_code == 200
    assert b'Sudoku Game' in response.data


def test_new_game_route_returns_puzzle_and_stores_solution():
    client = app_module.app.test_client()
    response = client.get('/new?clues=35')

    assert response.status_code == 200
    data = response.get_json()
    assert 'puzzle' in data

    puzzle = data['puzzle']
    assert len(puzzle) == 9
    assert all(len(row) == 9 for row in puzzle)
    assert app_module.CURRENT['puzzle'] == puzzle
    assert app_module.CURRENT['solution'] is not None


def test_check_route_accepts_correct_board():
    client = app_module.app.test_client()
    puzzle, solution = app_module.sudoku_logic.generate_puzzle(35)
    app_module.CURRENT['puzzle'] = puzzle
    app_module.CURRENT['solution'] = solution

    response = client.post('/check', json={'board': solution})

    assert response.status_code == 200
    assert response.get_json() == {'incorrect': []}


def test_check_route_identifies_incorrect_user_entry():
    client = app_module.app.test_client()
    puzzle, solution = app_module.sudoku_logic.generate_puzzle(35)
    app_module.CURRENT['puzzle'] = puzzle
    app_module.CURRENT['solution'] = solution

    board = app_module.sudoku_logic.deep_copy(solution)
    row, col = next(
        (row, col)
        for row in range(app_module.sudoku_logic.SIZE)
        for col in range(app_module.sudoku_logic.SIZE)
        if puzzle[row][col] == 0
    )
    board[row][col] = 1 if solution[row][col] != 1 else 2

    response = client.post('/check', json={'board': board})

    assert response.status_code == 200
    assert [row, col] in response.get_json()['incorrect']


def test_check_route_does_not_mark_correct_user_entry_incorrect():
    client = app_module.app.test_client()
    puzzle, solution = app_module.sudoku_logic.generate_puzzle(35)
    app_module.CURRENT['puzzle'] = puzzle
    app_module.CURRENT['solution'] = solution

    board = app_module.sudoku_logic.deep_copy(solution)
    row, col = next(
        (row, col)
        for row in range(app_module.sudoku_logic.SIZE)
        for col in range(app_module.sudoku_logic.SIZE)
        if puzzle[row][col] == 0
    )

    response = client.post('/check', json={'board': board})

    assert response.status_code == 200
    assert [row, col] not in response.get_json()['incorrect']


def test_check_route_with_no_active_game_returns_400():
    client = app_module.app.test_client()
    app_module.CURRENT['solution'] = None

    response = client.post('/check', json={'board': [[0 for _ in range(9)] for _ in range(9)]})

    assert response.status_code == 400
    assert response.get_json()['error'] == 'No game in progress'


def test_new_game_route_supports_difficulty_levels():
    client = app_module.app.test_client()

    for difficulty, expected_clues in {'easy': 45, 'medium': 35, 'hard': 25}.items():
        response = client.get(f'/new?difficulty={difficulty}')
        assert response.status_code == 200
        puzzle = response.get_json()['puzzle']
        clue_count = sum(1 for row in puzzle for cell in row if cell != 0)
        assert clue_count == expected_clues
        assert app_module.CURRENT['solution'] is not None


def test_hint_route_returns_one_empty_editable_cell():
    client = app_module.app.test_client()
    puzzle, solution = app_module.sudoku_logic.generate_puzzle(35)
    app_module.CURRENT['puzzle'] = puzzle
    app_module.CURRENT['solution'] = solution

    board = app_module.sudoku_logic.deep_copy(puzzle)
    response = client.post('/hint', json={'board': board})

    assert response.status_code == 200
    hint = response.get_json()
    assert puzzle[hint['row']][hint['col']] == 0
    assert board[hint['row']][hint['col']] == 0
    assert hint['value'] == solution[hint['row']][hint['col']]


def test_hint_route_does_not_overwrite_existing_user_entries():
    client = app_module.app.test_client()
    puzzle, solution = app_module.sudoku_logic.generate_puzzle(35)
    app_module.CURRENT['puzzle'] = puzzle
    app_module.CURRENT['solution'] = solution

    board = app_module.sudoku_logic.deep_copy(puzzle)
    empty_cells = [
        (row, col)
        for row in range(app_module.sudoku_logic.SIZE)
        for col in range(app_module.sudoku_logic.SIZE)
        if puzzle[row][col] == 0
    ]
    first_row, first_col = empty_cells[0]
    board[first_row][first_col] = 9
    response = client.post('/hint', json={'board': board})

    assert response.status_code == 200
    hint = response.get_json()
    assert (hint['row'], hint['col']) != (first_row, first_col)


def test_hint_route_with_no_active_game_returns_400():
    client = app_module.app.test_client()
    app_module.CURRENT['puzzle'] = None
    app_module.CURRENT['solution'] = None

    response = client.post('/hint', json={'board': [[0 for _ in range(9)] for _ in range(9)]})

    assert response.status_code == 400
    assert response.get_json()['error'] == 'No game in progress'
