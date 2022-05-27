from src import *

if __name__ == '__main__':
    xs, ys = read_iris()
    dt = CartTree()
    dt.fit(xs, ys)
    dt.score(xs, ys)
