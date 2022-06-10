import logging
from collections import Counter
from tqdm.auto import tqdm


class TreeNode:
    def __init__(self, ka, kv, res, lc, rc, depth=1):
        for k, v in locals().items():
            setattr(self, k, v)


def gini(arr):
    counter = Counter(arr)
    res, n = 1.0, len(arr)
    for num in counter.values():
        p = num / n
        res -= p ** 2
    return res


def split(xs, ys, attr, v):
    xl, yl = [], []
    xr, yr = [], []
    for i, x in enumerate(xs):
        if x[attr] <= v:
            xl.append(x)
            yl.append(ys[i])
        else:
            xr.append(x)
            yr.append(ys[i])
    return {
        'l': (xl, yl),
        'r': (xr, yr)
    }


class CartTree:
    def __init__(self, max_depth=18):
        self.root = None
        self.max_depth = max_depth

    def fit(self, xs, ys):
        print(f'Start training tree..')
        self.root = self.build(xs, ys, 1)

    def build(self, xs, ys, depth):
        cur_gini = gini(ys)
        n = len(ys)

        best_gain = 0.
        best_attr = None
        best_val = None
        best_split = None

        if depth <= self.max_depth:
            for attr in range(len(xs[0])):
                vals = set(x[attr] for x in xs)
                for v in tqdm(vals):
                    sped = split(xs, ys, attr, v)
                    s1, s2 = sped['l'], sped['r']
                    if not (len(s1[1]) and len(s2[1])):
                        continue
                    p0 = float(len(s1[1])) / n
                    gain = cur_gini - p0 * gini(s1[1]) - (1 - p0) * gini(s2[1])
                    if gain > best_gain:
                        best_gain = gain
                        best_attr = attr
                        best_val = v
                        best_split = (s1, s2)

        if depth <= self.max_depth and best_gain > 0:
            return TreeNode(ka=best_attr, kv=best_val, res=None,
                            lc=self.build(*best_split[0], depth=depth + 1),
                            rc=self.build(*best_split[1], depth=depth + 1), depth=depth)
        else:
            return TreeNode(ka=None, kv=None, lc=None, rc=None, res=Counter(ys), depth=depth)

    def pred(self, node, x):
        if node.res is not None:
            res_counter = Counter(node.res)
            return max(res_counter, key=res_counter.get)
        return self.pred(node.lc if x[node.ka] <= node.kv else node.rc, x)

    def predict(self, xs):
        return [self.pred(self.root, x) for x in xs]

    def score(self, xs, ys):
        res = self.predict(xs)
        n, m = 0, len(ys)
        for i in range(m):
            n += int(res[i] == ys[i])
        print('{}/{}, Acc: {:.2f}%'.format(int(n), m, (100. * n) / m))
