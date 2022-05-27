import pandas as pd

from ..util import *


def read_iris():
    res = pd.read_csv(BASE_PATH / 'data/iris.data', header=None)
    xs = res.iloc[:, :-1].to_numpy()
    ys = res.iloc[:, -1].tolist()
    return xs, ys
