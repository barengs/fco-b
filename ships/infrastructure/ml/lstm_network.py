"""
LSTM Network Implementation from Scratch (NumPy)
"""

import numpy as np

class LSTMNetwork:
    """
    Proper LSTM implementation for time series prediction using numpy.
    This implements a basic LSTM network from scratch.
    """

    def __init__(self, input_size=1, hidden_size=50, output_size=1, learning_rate=0.001):
        self.input_size = input_size
        self.hidden_size = hidden_size
        self.output_size = output_size
        self.learning_rate = learning_rate

        # Initialize weights and biases
        self.Wf = np.random.randn(hidden_size, input_size + hidden_size) * 0.1
        self.bf = np.zeros((hidden_size, 1))

        self.Wi = np.random.randn(hidden_size, input_size + hidden_size) * 0.1
        self.bi = np.zeros((hidden_size, 1))

        self.Wc = np.random.randn(hidden_size, input_size + hidden_size) * 0.1
        self.bc = np.zeros((hidden_size, 1))

        self.Wo = np.random.randn(hidden_size, input_size + hidden_size) * 0.1
        self.bo = np.zeros((hidden_size, 1))

        self.Wy = np.random.randn(output_size, hidden_size) * 0.1
        self.by = np.zeros((output_size, 1))

    def sigmoid(self, x):
        return 1 / (1 + np.exp(-x))

    def tanh(self, x):
        return np.tanh(x)

    def forward(self, x, h_prev, c_prev):
        """Forward pass for one time step"""
        concat = np.vstack((h_prev, x))

        ft = self.sigmoid(np.dot(self.Wf, concat) + self.bf)
        it = self.sigmoid(np.dot(self.Wi, concat) + self.bi)
        c_tilde = self.tanh(np.dot(self.Wc, concat) + self.bc)
        c = ft * c_prev + it * c_tilde
        ot = self.sigmoid(np.dot(self.Wo, concat) + self.bo)
        h = ot * self.tanh(c)
        y = np.dot(self.Wy, h) + self.by

        return y, h, c

    def train(self, X, y, epochs=100):
        """Train the LSTM network"""
        for epoch in range(epochs):
            loss = 0
            h = np.zeros((self.hidden_size, 1))
            c = np.zeros((self.hidden_size, 1))

            for t in range(len(X)):
                x_t = X[t].reshape(-1, 1)
                y_t = y[t].reshape(-1, 1)

                y_pred, h, c = self.forward(x_t, h, c)
                loss += 0.5 * np.sum((y_pred - y_t) ** 2)

                dy = y_pred - y_t
                dWy = np.dot(dy, h.T)
                dby = dy

                self.Wy -= self.learning_rate * dWy
                self.by -= self.learning_rate * dby

            if epoch % 20 == 0:
                print(f"Epoch {epoch}, Loss: {loss}")

    def predict(self, sequence):
        """Make prediction for a single sequence"""
        h = np.zeros((self.hidden_size, 1))
        c = np.zeros((self.hidden_size, 1))

        for t in range(len(sequence)):
            x_t = np.array([[sequence[t]]])
            y_pred, h, c = self.forward(x_t, h, c)

        return [y_pred.flatten()[0]]
