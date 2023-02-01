with open('sample_game.pgn','r') as f:
    out = f.readlines()
    f.close()

out = [out[i].strip() for i in range(len(out))]
#print(out)

player = 0 if '"The11thTom"' in out[4] else 1
moves = ''
for k in range(13,len(out)):
    moves = moves + ' ' + out[k]

_moves = moves.split(' ')[1:]
m = []
for i in range(len(_moves)//3):
    m.append(_moves[i*3+1])
    m.append(_moves[i*3+2])
print(m)


from stockfish import Stockfish as sf

stockfish_instance = sf('stockfish_20011801_x64.exe')

import chess.pgn
from io import StringIO as sIO
game = chess.pgn.read_game(sIO(moves))
b = game.board()
for m_i in range(len(m)-1):
    move = b.push_san(m[m_i]) #get lan
    #print(move)
fen = b.fen()
print(fen)
print(b.outcome())
stockfish_instance.set_fen_position(fen)
print(stockfish_instance.get_board_visual())