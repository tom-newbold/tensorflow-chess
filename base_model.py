import tensorflow as tf
import numpy as np
import tensor_conversions.tensor_conversions as tenconv
import json

class Layer(tf.Module):
    def __init__(self, nodes_in: int, nodes_out: int, name: str=None):
        super().__init__(name=name)
        self.w = tf.Variable(tf.random.normal([nodes_in, nodes_out]), trainable=True, name='w', dtype=tf.float32) # weights
        self.b = tf.Variable(tf.zeros([nodes_out]), trainable=True, name='b', dtype=tf.float32) # biases
    
    def __call__(self, x: tf.Tensor) -> tf.Tensor:
        y = tf.linalg.matmul(tf.cast(x, tf.float32), self.w) + self.b
        return tf.nn.relu(y)

class TwoLayerModel(tf.Module):
    def __init__(self, name: str=None):
        super().__init__(name=name)
        self.layer_1 = Layer(64, 128)
        self.layer_2 = Layer(128, 128)
    
    def __call__(self, x: tf.Tensor) -> tf.Tensor:
        _x = self.layer_1(x)
        return self.layer_2(_x)

class ModelWrapper:
    def __init__(self):
        self.model_instance = TwoLayerModel(name='model_instanace')

    def __call__(self, fen: str) -> list[tf.Tensor, str]: # TODO REMOVE NUMPY FUNC
        t_in = tenconv.fen_to_tensor(fen)
        model_out = self.model_instance(tf.reshape(t_in, [1, 64])) # pass into module
        ideal_out = np.zeros((2, 8, 8))
        for z in range(2): # convert back to tensor, generate ideal tensor
            max = -1
            max_xyz = [-1, -1, -1]
            for y in range(8):
                for x in range(8):
                    i = z*64 + y*8 + x
                    e = model_out[0][i]
                    if e > max:
                        max = e
                        ideal_out[max_xyz[2]][max_xyz[1]][max_xyz[0]] = 0
                        ideal_out[z][y][x] = 1
                        max_xyz = [x, y, z] # is x, y orientation correct? TODO

        ideal_out = tf.convert_to_tensor(ideal_out)
        t_out = tf.reshape(model_out, [2, 8, 8])
        return [tf.linalg.normalize(t_out)[0], tenconv.tensor_to_lan(ideal_out)]

MOVE_TREE = open('bin\\inital_dataset_compressed.json', 'r')

from base_stockfish import SF # rewrite this, put in CSE class ??
def composite_loss(omega: float, target_tensor: tf.Tensor, output_tensor: tf.Tensor, player: int, fen: str, move: str, out: bool=True):
    e_sigma_delta = tf.reduce_sum(tf.square(tf.subtract(target_tensor, output_tensor)))
    e_delta_sigma = tf.reduce_sum(target_tensor)**2 - tf.reduce_sum(output_tensor)**2
    p = 64 # P_max, value tbd
    if fen in MOVE_TREE:
        for m in MOVE_TREE[fen][player]:
            if m['move'] == move:
                if out: print('in move tree')
                p = omega
    else:
        if SF().check_move(fen, move):
            if out: print('valid')
            p = 1
        elif out: print('invalid')
    return tf.abs(e_sigma_delta * e_delta_sigma * p) # remove abs??

def basic_loss(target_tensor: tf.Tensor, output_tensor: tf.Tensor) -> float:
    return tf.reduce_sum(tf.square(tf.subtract(target_tensor, output_tensor)))

def train(model_wrapper: ModelWrapper, context: dict[int, str, str, dict[str, int]], learning_rate: float=0.1) -> float:
    model = model_wrapper.model_instance
    target_t = tenconv.lan_to_tensor(context['following_move'])

    with tf.GradientTape(persistent=True) as grad_tape:
        model_out = model_wrapper(context['fen'])
        #print(model_out[0])
        print('model returned move: '+model_out[1])
        if SF().check_move(context['fen'], model_out[1]): print('valid') # TODO remove this line after testing

        # l = basic_loss(tf.cast(target_t, tf.float32), model_out[0])
        l = composite_loss(0.8, tf.cast(target_t, tf.float32), model_out[0], context['player'], context['fen'], model_out[1], False)

    for m in [model.layer_1, model.layer_2]:
        dw, db = grad_tape.gradient(l, [m.w, m.b])
        m.w.assign_sub(learning_rate * dw)
        m.b.assign_sub(learning_rate * db)
    del grad_tape
    return l

def train_loop(model_wrapper: ModelWrapper, data: list[dict]) -> None:
    data = [{
            "player": 0,
            "fen": "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1",
            "following_move": "e2e3" }]
    #for e in range(len(data)): _loss = train(model_wrapper, data[e])
    for e in range(20):
        print('EPOCH {}:'.format(e))
        _loss = train(model_wrapper, data[0], 0.1)
        print('loss: '+str(_loss.numpy()))


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
