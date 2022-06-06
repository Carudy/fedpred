import pickle
import random

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
    co.mo = mo

    attrs = list(range(4))
    dos = {}
    i = 1
    for attr_piece in np.array_split(attrs, 2):
        _do = DataOwner(co, attr_piece, i)
        dos[i] = _do
        i += 1
    split_iris(dos.values())

    mo.connect_dos(dos.values())
    co.connect_dos(dos.values())
    co.dos = dos

    return mo, co, dos


if __name__ == '__main__':
    mo, co, dos = init()
    mo.keyex()
    mo.send_enc_tree()

    xs, ys = read_iris()
    # mo.model.score(xs, ys)

    n = 0
    for i in range(len(ys)):
        res = mo.query(i)
        if res == ys[i]:
            n += 1
        else:
            print(i, res, ys[i])
    logger.info(f'Acc: {n * 100 / len(ys):.2f}%')
