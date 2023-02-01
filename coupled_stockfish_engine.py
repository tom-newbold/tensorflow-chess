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
        self.board = self.game.board()

    def run(self):
        #mline = [m.uci() for m in self.game.mainline_moves()]
        #print('SAN: '+str(self.game.mainline_moves()))
        mline = self.game.mainline_moves()
        print('SAN: '+str(mline))
        mline = list(mline)
        # move, response = ['','']
        for i in range(len(mline)):
            m = mline[i]
            m_san = self.board.san(m)
            self.board.push(m)
            self.stockfish_instance.make_moves_from_current_position([m.uci()])
            if i%2 == self.player: # player turn
                eval = self.stockfish_instance.get_evaluation()
                if eval['type']=='cp':
                    print(m_san+': '+str(eval['value'])+' centipawns')
                elif eval['type']=='mate':
                    print(m_san+': mate in '+str(eval['value']))
                else:
                    print('evaluation failed')
        return self.board

    def get_sf_board(self):
        return self.stockfish_instance.get_board_visual()

if __name__ == '__main__':
    sf = CoupledStockfish('stockfish-test\\sample_game.pgn', 'The111thTom')
    print('following player '+str(sf.player)+' (0:white;1:black)')
    b = sf.run()
    print(b.fen())
    print(b.outcome())
    print(sf.get_sf_board())