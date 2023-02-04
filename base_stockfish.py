STOCKFISH_PATH = 'stockfish_test\\stockfish_20011801_x64.exe'

from stockfish import Stockfish

class SF: ## put into coupled stockfish (make_move func)
    def __init__(self):
        self.stockfish_instance = Stockfish(path=STOCKFISH_PATH)

    def check_move(self, board_fen, move_lan):
        self.stockfish_instance.set_fen_position(board_fen)
        return self.stockfish_instance.is_move_correct(move_lan)