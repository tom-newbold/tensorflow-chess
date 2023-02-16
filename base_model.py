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

class SuperModel(tf.Module):
    def __init__(self, name: str=None):
        super().__init__(name=name)
        self.layers = []

    def __call__(self, x: tf.Tensor) -> tf.Tensor:
        for layer in self.layers:
            x = layer(x)
        return x

class TwoLayerModel(SuperModel):
    def __init__(self, in_nodes: int=64, hidden_nodes: int=192, out_nodes: int=128, name: str=None):
        super().__init__(name=name)
        self.layers.append(Layer(in_nodes, hidden_nodes))
        self.layers.append(Layer(hidden_nodes, out_nodes))

        #return self.layer[1](y)

class ThreeLayerModel(SuperModel):
    def __init__(self, in_nodes: int=64, hidden_nodes: int=96, out_nodes: int=128, name: str=None):
        super().__init__(name=name)
        self.layers.append(Layer(in_nodes, hidden_nodes))
        self.layers.append(Layer(hidden_nodes, hidden_nodes))
        self.layers.append(Layer(hidden_nodes, out_nodes))
    
    '''
    def __call__(self, x: tf.Tensor) -> tf.Tensor:
        y = self.layer_1(x)
        z = self.layer_2(y)
        return self.layer_3(z)
    '''

class ModelWrapper:
    def __init__(self):
        self.model_instance = TwoLayerModel(in_nodes=65, out_nodes=128, name='model_instanace')

    def __call__(self, fen: str) -> list[tf.Tensor, str]:
        position_ten, player = tenconv.fen_to_tensor(fen)
        row_tensor = tf.reshape(position_ten, [1, 64])
        player_tensor = tf.cast(tf.constant([[player]]), dtype=tf.float32)
        model_out = self.model_instance(tf.concat([row_tensor, player_tensor], 1)) # TODO PASS PLAYER IN HERE
        slices = [model_out[0][0:64], model_out[0][64:128]]
        max = [tf.reduce_max(slices[0]), tf.reduce_max(slices[1])]
        ideal_out = np.zeros((128)) # TODO check this is correct orientation
        for z in range(2): # convert back to tensor, generate ideal tensor
            s = slices[z]
            for i in range(64):
                if s[i] == max[z]:
                    ideal_out[64*z + i] = 1
                    break
        ideal_out = tf.convert_to_tensor(ideal_out)
        ideal_out = tf.reshape(ideal_out, (2, 8, 8))
        t_out = tf.reshape(model_out, (2, 8, 8))
        return [tf.linalg.normalize(t_out)[0], tenconv.tensor_to_lan(ideal_out)]

MOVE_TREE = open('bin\\inital_dataset_compressed.json', 'r')

from base_stockfish import SF # rewrite this, put in CSE class ??
def composite_loss(omega: float, target_tensor: tf.Tensor, output_tensor: tf.Tensor, player: int, fen: str, move: str, out: bool=True):
    e_sigma_delta = tf.reduce_sum(tf.square(tf.subtract(target_tensor, output_tensor)))
    e_delta_sigma = tf.reduce_sum(target_tensor)**2 - tf.reduce_sum(output_tensor)**2
    p = 128 # P_max, value tbd
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

def learning_curve(x: float) -> float:
    return x

def train(model_wrapper: ModelWrapper, context: dict[int, str, str, dict[str, int]], t: float, learning_rate: float=0.1) -> float:
    #print('jitter scale: '+str(t))
    jitter = False
    model = model_wrapper.model_instance
    #print(context)
    target_t = tenconv.lan_to_tensor(context['following_move'], context['player'])

    with tf.GradientTape(persistent=True) as grad_tape:
        model_out = model_wrapper(context['fen'])
        print('model returned move: '+model_out[1])
        ## if SF().check_move(context['fen'], model_out[1]): print('valid') # TODO remove this line after testing

        # l = basic_loss(tf.cast(target_t, tf.float32), model_out[0])
        loss = composite_loss(0.8, tf.cast(target_t, tf.float32), model_out[0], context['player'], context['fen'], model_out[1], False)

    for ly in model.layers:
        dw, db = grad_tape.gradient(loss, [ly.w, ly.b])
        if jitter:
            jitter_tensors = [tf.linalg.normalize(tf.random.normal(_d.shape))[0] for _d in [dw, db]]
            scaled_jitter_tensors = [tf.math.multiply(_jt, loss*t) for _jt in jitter_tensors]
            ly.w.assign_sub(learning_curve(learning_rate) * (dw + scaled_jitter_tensors[0]))
            ly.b.assign_sub(learning_curve(learning_rate) * (db + scaled_jitter_tensors[1]))
        else:
            ly.w.assign_sub(learning_curve(learning_rate) * dw)
            ly.b.assign_sub(learning_curve(learning_rate) * db)
        
    del grad_tape
    return loss

def train_loop(model_wrapper: ModelWrapper, data: list[dict], inital_time: float=0, delta_time: float=1) -> None:
    for p in range(5):
        print('PASS {}'.format(p))
        for e in range(len(data)):
            _loss = train(model_wrapper, data[e], 1) # t=1 just uses loss scaling on jitter
            print('\nEPOCH {}:'.format(e))
    
    ''' # Test Loop
    data = [{
            "player": 0,
            "fen": "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1",
            "following_move": "e2e3" }]

    for e in range(20):
        print('\nEPOCH {}:'.format(e))
        t = inital_time + delta_time*float(e)
        _loss = train(model_wrapper, data[0], 1.5-t, 0.1) # tf.math.exp(-t).numpy()
        print('loss: '+str(_loss.numpy()))
    print('\nfinal tensor:')
    print(model_wrapper(data[0]['fen'])[0])
    '''


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
    
    #train_loop(model_wrap, [], 0, 0.05)
    data = json.load(open('bin\\out.json','r'))['data_points']
    train_loop(model_wrap, data[:100])

    while True:
        fen = input('fen string:')
        if fen.lower()[0] == 'e':
            # add saving functionality here
            break
        else:
            try: 
                #print(model_wrap(fen)[0])
                print('returned move: '+model_wrap(fen)[1])
            except: pass
