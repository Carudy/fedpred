import logging
import pickle
import random
import time

import numpy as np
from tqdm.auto import tqdm

from src import *


def train_iris():
    xs, ys = read_iris()
    dt = CartTree()
    dt.fit(xs, ys)
    dt.score(xs, ys)
    with (BASE_PATH / 'model/iris.tree').open('wb') as f:
        pickle.dump(dt, f)


def train_rna():
    xs, ys = read_libsvm('cod-rna')
    dt = CartTree()
    dt.fit(xs, ys)
    dt.score(xs, ys)
    with (BASE_PATH / 'model/rna.tree').open('wb') as f:
        pickle.dump(dt, f)


def init():
    co = Coodinator()

    with (BASE_PATH / 'model/rna.tree').open('rb') as f:
        dt = pickle.load(f)
    mo = ModelOwner(co, dt)
    co.mo = mo

    attrs = list(range(8))
    dos = {}
    i = 1
    for attr_piece in np.array_split(attrs, 3):
        _do = DataOwner(co, attr_piece, i)
        dos[i] = _do
        i += 1
    # split_iris(dos.values())
    split_libsvm(dos.values(), 'cod-rna')

    mo.connect_dos(dos.values())
    co.connect_dos(dos.values())
    co.dos = dos

    return mo, co, dos


if __name__ == '__main__':
    # mo, co, dos = init()
    # mo.keyex()
    # mo.send_enc_tree()
    # #
    xs, ys = read_libsvm('cod-rna')
    # mo.model.score(xs, ys)
    #
    # xp = []
    # yp = []
    # st = time.time()
    #
    # n = 0
    # for i in tqdm(range(len(ys))):
    #     res = mo.query(i)
    #     if res == ys[i]:
    #         n += 1
    #     else:
    #         # print(i, res, ys[i])
    #         pass
    #     if (i + 1) % 20 == 0:
    #         _t = time.time() - st
    #         xp.append(i + 1)
    #         yp.append(_t)
    #     if i >= 400:
    #         break
    # logger.info(f'Acc: {n * 100 / len(ys):.2f}%')
    #
    # with open(BASE_PATH / 'tmp.txt', 'w', encoding='utf-8') as fp:
    #     fp.write(f'{xp}\n\n{yp}')