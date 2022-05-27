from ..alg import *


class Coodinator:
    def __init__(self):
        self.sign_key, self.verify_key = gen_sign_key()
