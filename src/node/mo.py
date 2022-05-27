from ..alg import *


class ModelOwner:
    def __init__(self, model, co):
        self.sign_key, self.verify_key = gen_sign_key()
        self.model = model
        self.co = co

    def send_enc_tree(self):
        pass
