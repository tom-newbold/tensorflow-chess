import tensorflow as tf
import numpy as np

def fen_to_tensor(fen_string: str) -> tf.Tensor:
    map = { 'p':1, 'n':2, 'b':3, 'r':4, 'q':5, 'k':6 }
    array = np.zeros((8,8))
    rows = fen_string.split(' ')[0].split('/')
    for y in range(8):
        for x in range(8):
            piece = rows[y][x]
            try:
                val = int(piece)
                if val!=0:
                    rows[y] = rows[y][:x] + val*'0' + rows[y][x+1:]
                for i in range(val):
                    array[x+i, y] = 0
                x += val
            except ValueError:
                val = map[piece.lower()]
                array[x, y] = val if piece.isupper() else -val
    #output = tf.Variable(tf.zeros([8, 8], tf.int32))
    output = tf.convert_to_tensor(array.transpose())
    return output

#print(fen_to_tensor("r1bq2nr/2pk1Bpp/p4p2/np2p3/1P3P2/PQP1P2P/6P1/R1B1K1NR w KQ - 3 14"))

def lan_to_tensor(lan_string: str, player: int) -> tf.Tensor:
    a = np.zeros((2, 8, 8))
    if 'O-O' in lan_string: # special case for castling; [e1h1-f1g1, e8h8-f8g8]
        rank = 1 if player==0 else 8
        if lan_string == 'O-O-O': # queenside castle; [e1a1-c1d1, e8a8-c8d8]
            a[0, 8-rank, 4] = 1
            a[0, 8-rank, 0] = 1
            a[1, 8-rank, 2] = 1
            a[1, 8-rank, 3] = 1
        else:
            a[0, 8-rank, 4] = 1
            a[0, 8-rank, 7] = 1
            a[1, 8-rank, 5] = 1
            a[1, 8-rank, 6] = 1
    else:
        lan_string = lan_string.strip('+')
        if '-' in lan_string:
            lan_string = lan_string.split('-')
        elif 'x' in lan_string:
            lan_string = lan_string.split('x')
        s = [lan_string[0][-2:], lan_string[1]]
        for i in range(2):
            a[i, 8-int(s[i][1]), 'abcdefgh'.index(s[i][0])] = 1
    return tf.convert_to_tensor(a)

def tensor_to_lan(tensor: tf.Tensor) -> str:
    out = ''
    t = tensor.numpy()
    # check for case of castling
    for i in [7,0]:
        if t[0, i, 4] + t[0, i, 7] + t[1, i, 5] + t[1, i, 6] == 4: # castle
            return 'O-O'
        if t[0, i, 4] + t[0, i, 0] + t[1, i, 2] + t[1, i, 3] == 4: # castle queenside
            return 'O-O-O'
    for d in range(2):
        for y in range(8):
            for x in range(8):
                if t[d][y][x] == 1:
                    out += 'abcdefgh'[x] + str(8-y)
    return out # no prefix/capture consideration?

#print(tensor_to_lan(lan_to_tensor('a1h8')))
#print(tensor_to_lan(lan_to_tensor('a1-h8')))