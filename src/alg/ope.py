def get_ope(param):
    ps = []
    d = 1 << 4
    while len(ps) < 3:
        now = 0
        while not now:
            param //= d
            now = param & d
        ps.append(now)
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
