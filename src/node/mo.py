import copy
import pickle
import random
import grpc
from collections import defaultdict

from ..alg import *
from ..proto import *


class ModelOwner:
    def __init__(self, co, model, margin=5):
        self.enc_box = None
        self.enc_tree = None
        self.stub = None
        for k, v in locals().items():
            setattr(self, k, v)

        self.sign_key, self.verify_key = gen_sign_key()
        self.sign_msg = fedpred_pb2.Sign(ct=self.sign_key.sign(b'mo'), pk=self.verify_key, msg=b'mo')
        self.secret = random.choice(range(1000))
        self.hello_msg = fedpred_pb2.HelloMsg(sign=self.sign_msg, r=self.secret)
        self.ka_map = {}

    def connect_dos(self, dos):
        self.stub = {}
        for do in dos:
            channel = grpc.insecure_channel(f'{do.addr}:{do.port}')
            self.stub[do.name] = fedpred_pb2_grpc.FedPredStub(channel)
            for attr in do.data.keys():
                self.ka_map[attr] = do.name

    def keyex(self):
        self.enc_box = {}
        for name, stub in self.stub.items():
            res = stub.keyex(self.hello_msg)
            _s = str(res.r).encode()
            self.enc_box[name] = kdf_box(str(self.secret).encode(), _s)

    def send_enc_tree(self):
        cnt = 0
        self.node_map = {}
        self.enc_tree = copy.deepcopy(self.model.root)

        def dfs(node, ori):
            nonlocal cnt
            node.pos = cnt
            ori.pos = cnt
            self.node_map[cnt] = ori
            cnt += 1
            if node.res is None:
                node.ka = sha256(node.ka)
                node.kv = None
                dfs(node.lc, ori.lc)
                dfs(node.rc, ori.rc)

        dfs(self.enc_tree, self.model.root)
        self.co.receive_model(pickle.dumps(self.enc_tree))

    def query(self, x):
        leaf_id = self.co.query(x)
        c = self.node_map[leaf_id].res
        return max(c, key=c.get)
