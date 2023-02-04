with open('sample_game.pgn','r') as f:
    out = f.readlines()
    f.close()

out = [out[i].strip() for i in range(len(out))]

player = 0 if '"The111thTom"' in out[4] else 1
moves = '' # pgn string
for k in range(13,len(out)):
    moves = moves + ' ' + out[k]

_moves = moves.split(' ')[1:]
m = [] # array of moves
for i in range(len(_moves)//3):
    m.append(_moves[i*3+1])
    m.append(_moves[i*3+2])
print(' '.join(m))

###

move_pairs = [] # pairs move with response
if player==1:
    move_pairs.append([m[0]])
for k in range(len(m)//2):
    p = player + k*2
    move_pairs.append(m[p:p+2])
print(move_pairs)

## runs game; eval at each move
from stockfish import Stockfish as sf
stockfish_instance = sf('stockfish_20011801_x64.exe')

import chess.pgn
from io import StringIO as sIO
game = chess.pgn.read_game(sIO('1.'))
b = game.board()

for m_i in range(len(move_pairs)):
    try:
        move, response = move_pairs[m_i]
    except ValueError: # where no pair exists
        move = move_pairs[m_i][0]
        if move=='1-0': break
        stockfish_instance.make_moves_from_current_position([b.push_san(move)])
        continue
    if move=='1-0': break
    stockfish_instance.make_moves_from_current_position([b.push_san(move)])
    print(stockfish_instance.get_evaluation()['value']) # eval move
    if response=='1-0': break
    stockfish_instance.make_moves_from_current_position([b.push_san(response)])
print(b.outcome())
#fen = b.fen()
#stockfish_instance.set_fen_position(fen)
print(stockfish_instance.get_board_visual())