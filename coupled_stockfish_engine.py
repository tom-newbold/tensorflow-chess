STOCKFISH_PATH = 'stockfish_test\\stockfish_20011801_x64.exe'

from stockfish import Stockfish
import chess.pgn as pgn

#?
from io import StringIO

class CoupledStockfish:
    def __init__(self, pgn_path, username, out=True):
        self.stockfish_instance = Stockfish(path=STOCKFISH_PATH)
        self.games = []
        try:
            f = open(pgn_path, encoding='utf-8')
            g = pgn.read_game(f)
            while not (g is None):
                self.games.append(g)
                g = pgn.read_game(f)
        except FileNotFoundError:
            self.games = [pgn.read_game(StringIO('1.'))] ## add support for regular json input (need player input)
        self.player = []
        for i in range(len(self.games)):
            if self.games[i].headers['White'] == username:
                self.player.append(0)
            elif self.games[i].headers['Black'] == username:
                self.player.append(1)
            else:
                self.player.append(-1)
        self.output = out

    def make_move(self, board, move, eval=False):
        board.push(move)
        self.stockfish_instance.make_moves_from_current_position([move.uci()])
        if eval:
            return self.stockfish_instance.get_evaluation()
        ## TODO: return exception if move invalid??

    def run(self, game_id=0):
        out = []
        mline = self.games[game_id].mainline_moves()
        if self.output: print('SAN: '+str(mline))
        mline = list(mline)
        b = self.games[game_id].board()
        for i in range(len(mline)):
            m = mline[i]
            m_san = b.lan(m)
            m_lan = b.san(m)
            if i%2 == self.player[game_id]: # player turn
                fen_context = b.fen()
                eval = self.make_move(b, m, eval=True)
                if self.output:
                    if eval['type']=='cp':
                        print(m_san+': '+str(eval['value'])+' centipawns')
                    elif eval['type']=='mate':
                        print(m_san+': mate in '+str(eval['value']))
                    else:
                        print('evaluation failed')
                out.append({
                    'fen':fen_context,
                    'move':m_lan,
                    'eval':eval
                })
                ## extract state here and eval position; add to database
            else:
                self.make_move(b, m)
        return (out, b)

    def get_sf_board(self):
        return self.stockfish_instance.get_board_visual()

if __name__ == '__main__':
    sf = CoupledStockfish('stockfish_test\\sample_game.pgn', 'The111thTom')
    print('following player '+str(sf.player)+' (0:white;1:black)')
    b = sf.run()[1]
    print(b.fen())
    print(b.outcome())
    print(sf.get_sf_board())
    # TODO: import more games from chess.com api
    #       or use separate files