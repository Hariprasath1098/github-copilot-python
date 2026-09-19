from flask import Flask, render_template, jsonify, request
import sudoku_logic

app = Flask(__name__)

DIFFICULTY_CLUES = {
    'easy': 45,
    'medium': 35,
    'hard': 25,
}

# Keep a simple in-memory store for current puzzle and solution
CURRENT = {
    'puzzle': None,
    'solution': None
}

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/new')
def new_game():
    difficulty = (request.args.get('difficulty') or '').lower()
    clues = request.args.get('clues')
    if clues is None:
        clues = DIFFICULTY_CLUES.get(difficulty, 35)
    else:
        clues = int(clues)
    puzzle, solution = sudoku_logic.generate_puzzle(clues)
    CURRENT['puzzle'] = puzzle
    CURRENT['solution'] = solution
    return jsonify({'puzzle': puzzle})

@app.route('/check', methods=['POST'])
def check_solution():
    data = request.json
    board = data.get('board')
    solution = CURRENT.get('solution')
    if solution is None:
        return jsonify({'error': 'No game in progress'}), 400
    incorrect = []
    for i in range(sudoku_logic.SIZE):
        for j in range(sudoku_logic.SIZE):
            if board[i][j] != solution[i][j]:
                incorrect.append([i, j])
    return jsonify({'incorrect': incorrect})

@app.route('/hint', methods=['POST'])
def get_hint():
    data = request.json
    board = data.get('board')
    puzzle = CURRENT.get('puzzle')
    solution = CURRENT.get('solution')
    if puzzle is None or solution is None:
        return jsonify({'error': 'No game in progress'}), 400

    hint = sudoku_logic.get_hint(board, puzzle, solution)
    if hint is None:
        return jsonify({'error': 'No empty cells available'}), 400

    row, col, value = hint
    return jsonify({'row': row, 'col': col, 'value': value})

if __name__ == '__main__':
    app.run(debug=True)