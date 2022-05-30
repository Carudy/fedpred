import pandas as pd

from ..util import *
from ..alg import *


def read_iris():
    res = pd.read_csv(BASE_PATH / 'data/iris.data', header=None)
    xs = res.iloc[:, :-1].to_numpy()
    ys = res.iloc[:, -1].tolist()
    return xs, ys


def split_iris(do_list):
    res = pd.read_csv(BASE_PATH / 'data/iris.data', header=None)
    xs = res.iloc[:, :-1]
    for do in do_list:
        do.data = {}
        for attr in do.attrs:
            ka = sha256(attr)
            do.data[ka] = xs.iloc[:, attr].tolist()
