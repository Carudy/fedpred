import pickle

import numpy as np

from src import *


def train_iris():
    xs, ys = read_iris()
    dt = CartTree()
    dt.fit(xs, ys)
    dt.score(xs, ys)
    with (BASE_PATH / 'model/iris.tree').open('wb') as f:
        pickle.dump(dt, f)


def init():
    co = Coodinator()

    with (BASE_PATH / 'model/iris.tree').open('rb') as f:
        dt = pickle.load(f)
    mo = ModelOwner(co, dt)

    attrs = list(range(4))
    dos = []
    i = 1
    for attr_piece in np.array_split(attrs, 2):
        _do = DataOwner(co, attr_piece, i)
        i += 1
        dos.append(_do)
    split_iris(dos)

    mo.connect_dos(dos)

    return mo, co, dos


if __name__ == '__main__':
    mo, co, dos = init()
    mo.keyex()
    mo.send_enc_tree()
