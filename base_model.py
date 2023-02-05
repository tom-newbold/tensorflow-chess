import tensorflow as tf
import numpy as np
import tensor_conversions.tensor_conversions as tenconv
import json

class Layer(tf.Module):
    def __init__(self, nodes_in, nodes_out, name=None):
        super().__init__(name=name)
        self.w = tf.Variable(tf.random.normal([nodes_in, nodes_out]), name='w', dtype=tf.float32) # weights
        self.b = tf.Variable(tf.zeros([nodes_out]), name='b', dtype=tf.float32) # biases
    
    def __call__(self, x):
        y = tf.linalg.matmul(tf.cast(x, tf.float32), self.w) + self.b
        return tf.nn.relu(y)

class TwoLayerModel(tf.Module):
    def __init__(self, name=None):
        super().__init__(name=name)
        self.layer_1 = Layer(64, 128)
        self.layer_2 = Layer(128, 128)
    
    def __call__(self, x):
        _x = self.layer_1(x)
        return self.layer_2(_x)

class ModelWrapper:
    def __init__(self):
        self.model_instance = TwoLayerModel(name='model_instanace')

    def __call__(self, fen):
        t_in = tenconv.fen_to_tensor(fen).numpy()
        model_in = tf.constant([[t_in[x, y] for x in range(8) for y in range(8)]]) # convert to column vector
        model_out = self.model_instance(model_in) # pass into module
        #print(model_out)
        t_out = np.zeros((2, 8, 8))
        ideal_out = np.zeros((2, 8, 8))
        for z in range(2): # convert back to tensor, generate ideal tensor
            max = -1
            max_xyz = [-1, -1, -1]
            for y in range(8):
                for x in range(8):
                    i = z*64 + y*8 + x
                    e = model_out[0][i]
                    t_out[z][y][x] = e
                    if e > max:
                        max = e
                        ideal_out[max_xyz[2]][max_xyz[1]][max_xyz[0]] = 0
                        ideal_out[z][y][x] = 1
                        max_xyz = [x, y, z] # is x, y orientation correct? TODO

        t_out = tf.convert_to_tensor(t_out)
        ideal_out = tf.convert_to_tensor(ideal_out)
        return [t_out, tenconv.tensor_to_lan(ideal_out)]

MOVE_TREE = open('bin\\inital_dataset_compressed.json', 'r')

from base_stockfish import SF # rewrite this, put in CSE class ??
def composite_loss(omega, target_tensor, output_tensor, player, fen, move):
    e_sigma_delta = tf.reduce_sum(tf.square(tf.subtract(target_tensor, output_tensor))).numpy()
    e_delta_sigma = (tf.reduce_sum(target_tensor).numpy())**2 - (tf.reduce_sum(output_tensor).numpy())**2
    p = 128 # P_max, value tbd
    if fen in MOVE_TREE:
        for m in MOVE_TREE[fen]:
            if m['move'] == move:
                print('in move tree')
                p = omega
    else:
        if SF().check_move(fen, move):
            print('valid')
            p = 1
        else: print('invalid')
    return e_sigma_delta * e_delta_sigma * p

def train(model_wrapper, context, learning_rate=0.1):
    target_t = tenconv.lan_to_tensor(context['following_move'])
    model_out = model_wrapper(context['fen'])
    l = composite_loss(0.8, target_t, model_out[0], context['player'], context['fen'], model_out[1])
    model = model_wrapper.model_instance
    for m in [model.layer_1, model.layer_2]:
        dw, db = tf.GradientTape().gradient(l, [m.w, m.b])
        m.w.assign_sub(learning_rate * dw)
        m.b.assign_sub(learning_rate * db)
    return l

def train_loop(model_wrapper, data):
    data = [{
            "player": 0,
            "fen": "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1",
            "following_move": "e2e3" }]
    #for e in range(len(data)):
    for e in range(20):
        _loss = train(model_wrapper, data[0])
        print(_loss)
    return


if __name__ == '__main__':
    model_wrap = ModelWrapper()
    print('model initialised')
    '''
    test_fen = 'rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1'
    out = model(test_fen) # should return opening when trained
    print(out[1])
    l = composite_loss(0.8, tenconv.lan_to_tensor('e2e4'), out[0], 0, test_fen, out[1])
    print(l)
    '''
    #data = json.load(open('bin\\inital_dataset.json','r'))['data_points']
    train_loop(model_wrap, [])
