import tensorflow as tf
import numpy as np

def fen_to_tensor(fen_string):
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
                array[x, y] = val if piece.islower() else -val
    #output = tf.Variable(tf.zeros([8, 8], tf.int32))
    output = tf.convert_to_tensor(array.transpose())
    return output

#print(fen_to_tensor("r1bq2nr/2pk1Bpp/p4p2/np2p3/1P3P2/PQP1P2P/6P1/R1B1K1NR w KQ - 3 14"))

def tensor_to_lan(tensor):
    out = ''
    t = tensor.numpy()
    for d in range(2):
        for y in range(8):
            for x in range(8):
                if t[d][y][x] == 1:
                    out += 'abcdefgh'[x] + str(8-y) # is y right here?
    return out

a = np.zeros((2, 8, 8)) # dim, y(num), x(letter)
a[0, 6, 4] = 1 #e2
a[1, 4, 4] = 1 #e4

print(tensor_to_lan(tf.convert_to_tensor(a)))