STOCKFISH_PATH = 'stockfish-test\\stockfish_20011801_x64.exe'

from stockfish import Stockfish
import chess.pgn as pgn

#?
from io import StringIO

class CoupledStockfish:
    def __init__(self, pgn_path, username, out=True):
        self.stockfish_instance = Stockfish(path=STOCKFISH_PATH)
        try:
            g = pgn.read_game(open(pgn_path, encoding='utf-8'))
            while not (g is None):
                self.games.append(g)
                g = pgn.read_game(open(pgn_path, encoding='utf-8'))
        except FileNotFoundError:
            self.games = [pgn.read_game(StringIO('1.'))]
        self.game = pgn.read_game(open(pgn_path, encoding='utf-8')) # TODO: array for multiple games? and regular json input variation
        if self.game.headers['White'] == username:
            self.player = 0
        elif self.game.headers['Black'] == username:
            self.player = 1
        else:
            self.player = -1
        self.board = self.game.board()
        self.output = out

    def make_move(self, move, eval=False):
        self.board.push(move)
        self.stockfish_instance.make_moves_from_current_position([move.uci()])
        if eval:
            return self.stockfish_instance.get_evaluation()

    def run(self, game_id=0):
        out = []
        mline = self.games[game_id].mainline_moves()
        if self.output: print('SAN: '+str(mline))
        mline = list(mline)
        # move, response = ['','']
        for i in range(len(mline)):
            m = mline[i]
            m_san = self.board.san(m)
            if i%2 == self.player: # player turn
                fen_context = self.board.fen()
                eval = self.make_move(m, eval=True)
                if self.output:
                    if eval['type']=='cp':
                        print(m_san+': '+str(eval['value'])+' centipawns')
                    elif eval['type']=='mate':
                        print(m_san+': mate in '+str(eval['value']))
                    else:
                        print('evaluation failed')
                out.append({
                    'fen':fen_context,
                    'move':m_san,
                    'eval':eval
                })
                ## extract state here and eval position; add to database
            else:
                self.make_move(m)
        return (out, self.board)

    def get_sf_board(self):
        return self.stockfish_instance.get_board_visual()

if __name__ == '__main__':
    sf = CoupledStockfish('stockfish-test\\sample_game.pgn', 'The111thTom')
    print('following player '+str(sf.player)+' (0:white;1:black)')
    b = sf.run()
    print(b.fen())
    print(b.outcome())
    print(sf.get_sf_board())
    # TODO: import more games from chess.com api
    #       or use separate files