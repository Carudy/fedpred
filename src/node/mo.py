import copy
import pickle
import random
import grpc
from collections import defaultdict

from ..alg import *
from ..proto import *


class ModelOwner:
    def __init__(self, co, model, margin=5):
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
        self.enc_tree = copy.deepcopy(self.model.root)

        ranges = defaultdict(list)

        def dfs(node):
            if node.res is None:
                node.ka = sha256(node.ka)
                ranges[node.ka].append((node.kv - self.margin, node.kv + self.margin))
                node.kv = random.uniform(*ranges[node.ka][-1])
                doi = self.ka_map[node.ka]
                box = self.enc_box[doi]
                node.kv = box.encrypt(pickle.dumps(node.kv))
                dfs(node.lc)
                dfs(node.rc)
            else:
                node.res = None

        dfs(self.enc_tree)
        for ka, range in ranges.items():
            doi = self.ka_map[ka]
            logger.info(f'Sending margin to {doi}, ka: {ka}')
            box = self.enc_box[doi]
            msg = box.encrypt(pickle.dumps(range))
            self.stub[doi].enc_msg(fedpred_pb2.EncMsg(action='range', ct=msg))
