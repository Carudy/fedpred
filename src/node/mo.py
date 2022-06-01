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
        self.leaf_map = {}

        def dfs_leaf_number(node):
            nonlocal cnt
            if node.res is None:
                dfs_leaf_number(node.lc)
                dfs_leaf_number(node.rc)
            else:
                node.pos = cnt
                self.leaf_map[cnt] = node
                cnt += 1

        dfs_leaf_number(self.model.root)
        self.enc_tree = copy.deepcopy(self.model.root)

        kvs = defaultdict(list)
        ranges = defaultdict(list)

        def dfs(node, f=True):
            if node.res is None:
                if f:
                    node.ka = sha256(node.ka)
                    kvs[node.ka].append(node.kv)
                else:
                    for rg in ranges[ka]:
                        if rg[0] <= node.kv <= rg[1]:
                            node.kv = random.uniform(*rg)
                            doi = self.ka_map[node.ka]
                            box = self.enc_box[doi]
                            node.kv = box.encrypt(pickle.dumps(node.kv))
                            break
                dfs(node.lc)
                dfs(node.rc)
            else:
                if not f:
                    node.res = None

        dfs(self.enc_tree)

        for ka, vals in kvs.items():
            vals.sort()
            st = vals[0] - self.margin
            for i in range(len(vals) - 1):
                lens = vals[i + 1] - vals[i]
                if lens >= 3 * self.margin:
                    ed = vals[i] + self.margin
                    ranges[ka].append((st, ed))
                    st = vals[i + 1] - self.margin
                else:
                    ed = vals[i] + lens * 0.33
                    ranges[ka].append((st, ed))
                    st = vals[i + 1] - lens * 0.33
            ranges[ka].append((st, vals[-1] + self.margin))

        for ka, rg in ranges.items():
            doi = self.ka_map[ka]
            logger.info(f'Sending margin to {doi}, ka: {ka}')
            box = self.enc_box[doi]
            msg = box.encrypt(pickle.dumps({
                'ka': ka,
                'range': rg,
            }))
            self.stub[doi].enc_msg(fedpred_pb2.EncMsg(action='range', ct=msg))

        dfs(self.enc_tree, False)
