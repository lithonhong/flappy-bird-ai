import numpy as np
import scipy.special

from settings import *

class NeuralNetwork:
    def __init__(self, num_inputs, num_hidden, num_output):
        self.num_inputs = num_inputs
        self.num_hidden = num_hidden
        self.num_output = num_output
        self.weights_input_hidden = np.random.uniform(-1, 1, size=(self.num_hidden, self.num_inputs))
        self.weights_hidden_output = np.random.uniform(-1, 1, size=(self.num_output, self.num_hidden))
        self.activation_func = lambda x : scipy.special.expit(x)

    def get_output(self, get_inputs):
        if len(get_inputs) != self.num_inputs:
            raise ValueError()
        
        hidden_in = np.dot(self.weights_input_hidden, get_inputs)
        hidden_out = self.activation_func(hidden_in)
        final_in = np.dot(self.weights_hidden_output, hidden_out)
        final_out = self.activation_func(final_in)
        return final_out
    
    def mix_array(arr1, arr2):
        total_entries = arr1.size
        num_rows = arr1.shape[0]
        num_cols = arr1.shape[1]

        p1_gene_index = np.random.choice(np.arange(total_entries), size=int(total_entries * 0.5), replace=False)

        res = np.random.rand(num_rows, num_cols)

        for row in range(0, num_rows):
            for col in range(0, num_cols):
                index = row * num_cols + col
                if index in p1_gene_index:
                    res[row][col] = arr1[row][col]
                else:
                    res[row][col] = arr2[row][col]
        
        return res
    
    def modify_array(self, arr):
        for x in arr:
            if np.random.random() < GEN_MUTATION_RATIO:
                    x[...] = np.random.uniform(-0.5, 0.5, x.shape)

            else:
                for y in x:
                    y += (np.random.random() * 2 - 1) * GEN_MODIFY_RATIO
                    y = min(1, max(y, -1))

    def mutate(self):
        self.modify_array(self.weights_input_hidden)
        self.modify_array(self.weights_hidden_output)
    
    def copy(self):
        child = NeuralNetwork(self.num_inputs, self.num_hidden, self.num_output)
        child.weights_input_hidden = np.copy(self.weights_input_hidden)
        child.weights_hidden_output = np.copy(self.weights_hidden_output)

        return child