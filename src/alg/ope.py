def get_ope(param):
    ps = []
    d = (1 << 16) - 1
    while len(ps) < 3:
        now = 0
        while not now:
            now = param & d
            param //= d
        ps.append((now >> 6) / max((now & ((1<<6)-1), 1)))
    return OPF(*ps)


class OPF:
    def __init__(self, a, b, c):
        for k, v in locals().items():
            setattr(self, k, v)

    def __call__(self, x):
        res = self.a * (x - self.c) ** 2 + self.b
        if x >= self.c:
            return res
        return 2 * self.b - res
