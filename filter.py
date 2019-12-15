import numpy as np
import torch as tr
import pandas as pd
import math
import matplotlib.pyplot as plt

# Neural network for filter definition


class NumericNet1(tr.nn.Module):
    def __init__(self, input_size):
        super(NumericNet1, self).__init__()
        self.l1 = tr.nn.Linear(input_size, 100)
        self.l2 = tr.nn.Linear(100, 20)
        self.l3 = tr.nn.Linear(20, 1)

    def forward(self, x):
        h1 = tr.sigmoid(self.l1(x))
        h2 = tr.tanh(self.l2(h1))
        y = self.l3(h2)
        return y


class NumericNet2(tr.nn.Module):
    def __init__(self, input_size):
        super(NumericNet2, self).__init__()
        self.l1 = tr.nn.Linear(input_size, input_size * 2)
        self.l2 = tr.nn.Linear(input_size * 2, 10)
        self.l3 = tr.nn.Linear(10, 1)

    def forward(self, x):
        h1 = tr.sigmoid(self.l1(x))
        h2 = tr.sigmoid(self.l2(h1))
        y = self.l3(h2)
        return y


class NumericNet3(tr.nn.Module):
    def __init__(self, input_size):
        super(NumericNet3, self).__init__()
        self.l1 = tr.nn.Linear(input_size, input_size * 2)
        self.l2 = tr.nn.Linear(input_size * 2, input_size)
        self.l3 = tr.nn.Linear(input_size, input_size//2)
        self.l4 = tr.nn.Linear(input_size//2, 1)

    def forward(self, x):
        h1 = tr.tanh(self.l1(x))
        h2 = tr.sigmoid(self.l2(h1))
        h3 = tr.tanh(self.l3(h2))
        y = self.l4(h3)
        return y


class NumericNet4(tr.nn.Module):
    def __init__(self, input_size):
        super(NumericNet4, self).__init__()
        self.l1 = tr.nn.Linear(input_size, 128)
        self.l2 = tr.nn.Linear(128, 64)
        self.l3 = tr.nn.Linear(64, 32)
        self.l4 = tr.nn.Linear(32, 16)
        self.l5 = tr.nn.Linear(16, 1)

    def forward(self, x):
        h1 = tr.sigmoid(self.l1(x))
        h2 = tr.tanh(self.l2(h1))
        h3 = tr.sigmoid(self.l3(h2))
        h4 = tr.tanh(self.l4(h3))
        y = self.l5(h4)
        return y


def to_tensor(df): return tr.tensor(df.values.astype(np.float32))


training_loss = []


def train_model(inputs, targets, net):
    # net = Net()
    optimizer = tr.optim.SGD(net.parameters(), lr=0.01/inputs.shape[0])
    num_epochs = 5000
    for epoch in range(num_epochs):
        # Start with zero gradient
        optimizer.zero_grad()

        # Calculate network output and sum of squared loss for each datapoint
        y = net(inputs)
        loss = (tr.abs(y.squeeze() - targets.squeeze())).sum()/(inputs.shape[0])

        training_loss.append(loss)

        # Calculate gradients and take a descent step
        loss.backward()
        optimizer.step()

        # Monitor optimization progress
        num_errors = (y.squeeze().round().detach().numpy()
                      != targets.numpy()).sum()
        if epoch % (num_epochs/10) == 0:
            print(loss, num_errors)
    return net


if __name__ == "__main__":
    df = pd.read_csv("./data/baseline_data.csv", index_col=0, header=None, names=[
                     '0', '1', '2', '3', '4', '5', '6', '7', '8', '9', '10', '11', '12', '13', '14', '15', '16'])
    # print(df)
    labels = df.pop('16')
    # print(labels)
    feature = df
    # print(feature)
    v = to_tensor(feature)
    t = to_tensor(labels)

    epochs = [i for i in range(5000)]

    nn1 = NumericNet1(16)
    training_loss.clear()
    nn1 = train_model(v, t, nn1)
    tr.save(nn1.state_dict(), './nn1')

    plt.plot(epochs, training_loss, 'r--')
    plt.xlabel('epochs')
    plt.ylabel('loss')
    plt.legend()
    plt.savefig('./nn1_loss.png')
    plt.clf()

    nn2 = NumericNet2(16)
    training_loss.clear()
    nn2 = train_model(v, t, nn2)
    tr.save(nn2.state_dict(), './nn2')

    plt.plot(epochs, training_loss, 'r--')
    plt.xlabel('epochs')
    plt.ylabel('loss')
    plt.legend()
    plt.savefig('./nn2_loss.png')
    plt.clf()


    nn3 = NumericNet3(16)
    training_loss.clear()
    nn3 = train_model(v, t, nn3)
    tr.save(nn3.state_dict(), './nn3')

    plt.plot(epochs, training_loss, 'r--')
    plt.xlabel('epochs')
    plt.ylabel('loss')
    plt.legend()
    plt.savefig('./nn3_loss.png')
    plt.clf()

    nn4 = NumericNet4(16)
    training_loss.clear()
    nn4 = train_model(v, t, nn4)
    tr.save(nn4.state_dict(), './nn4')

    plt.plot(epochs, training_loss, 'r--')
    plt.xlabel('epochs')
    plt.ylabel('loss')
    plt.legend()
    plt.savefig('./nn4_loss.png')
    plt.clf()
