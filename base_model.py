import tensorflow as tf
import tensor_conversions.tensor_conversions as tenconv

class Layer(tf.Module):
    def __init__(self, nodes_in, nodes_out, name=None):
        super().__init__(name=name)
        self.w = tf.Variable(tf.random.normal([nodes_in, nodes_out]), name='w') # weights
        self.b = tf.Variable(tf.zeros([nodes_out]), name='b') # biases
    
    def __call__(self, x):
        y = tf.matmul(x, self.w) + self.b
        return tf.nn.rect(y) # does this need rectifying?

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
        t_in = tenconv.fen_to_tensor(fen)
        t_out = self.model_instance(t_in)
        return tenconv.tensor_to_lan()


if __name__ == '__main__':
    model = ModelWrapper()
    print('model initialised')