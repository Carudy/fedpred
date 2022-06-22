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


def box_plot():
    xp = [-5, -1.2, 0.34, 1, 2.8, 12]
    yp = []
    for x in xp:
        print(f'for {x}')
        _y = []
        nn = 200
        for i in range(nn):
            ps = [random.randint(1, (1 << 16)) for _ in range(3)]
            for i in range(len(ps)):
                ps[i] = (ps[i] >> 6) / max((ps[i] & ((1 << 6)-1), 1))
            f = OPF(*ps)
            v = f(x)
            print(f'\t => {v}')
            _y.append(float(f'{v:.3f}'))
        yp.append(_y)
    with open(BASE_PATH / 'box.txt', 'w', encoding='utf-8') as fp:
        fp.write(f'{xp}\n\n{yp}')


def test_compute_time():
    xs, ys = read_libsvm('cod-rna')
    mo, co, dos = init()
    mo.keyex()
    mo.send_enc_tree()
    xp = []
    yp = []
    logger.info("Start test.")
    st = time.time()

    n = 0
    comm_arr = [0]
    for i in tqdm(range(len(ys))):
        res = mo.query(i, comm_arr)
        if res == ys[i]:
            n += 1
        else:
            # print(i, res, ys[i])
            pass
        if (i + 1) % 20 == 0:
            _t = time.time() - st
            xp.append(i + 1)
            yp.append(_t)
            comm_arr.append(0)
        if i >= 80:
            break
    logger.info(f'Acc: {n * 100 / len(ys):.2f}%')

    zp = [0] * len(comm_arr)
    for i in range(len(zp)):
        zp[i] = comm_arr[i] + zp[i-1]

    with open(BASE_PATH / 'tmp.txt', 'w', encoding='utf-8') as fp:
        fp.write(f'{xp}\n\n{yp}\n\n{zp[:len(xp)]}')

    xp = random.sample(range(len(xs)), 6)


if __name__ == '__main__':
    # mo, co, dos = init()
    # mo.keyex()
    # mo.send_enc_tree()
    # #
    # xs, ys = read_libsvm('cod-rna')
    # mo.model.score(xs, ys)
    test_compute_time()
