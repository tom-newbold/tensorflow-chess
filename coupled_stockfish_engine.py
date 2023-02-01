STOCKFISH_PATH = 'stockfish-test\\stockfish_20011801_x64.exe'

from stockfish import Stockfish
import chess.pgn as pgn

class CoupledStockfish:
    def __init__(self, pgn_path, username):
        self.stockfish_instance = Stockfish(path=STOCKFISH_PATH)
        self.game = pgn.read_game(open(pgn_path, encoding='utf-8'))
        if self.game.headers['White'] == username:
            self.player = 0
        elif self.game.headers['Black'] == username:
            self.player = 1
        else:
            self.player = -1

    def run(self):
        b = self.game.board()
        for m in self.game.mainline_moves():
            b.push(m)
        return b

if __name__ == '__main__':
    sf = CoupledStockfish('stockfish-test\\sample_game.pgn', 'The111thTom')
    print(sf.run().fen())
    print(sf.player)