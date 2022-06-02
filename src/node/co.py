import pickle
import grpc

from ..alg import *
from ..proto import *


class Coodinator:
    def __init__(self):
        self.sign_key, self.verify_key = gen_sign_key()
        self.model = None
        self.ka_map = {}
        self.stub = {}

    def receive_model(self, model):
        self.model = pickle.loads(model)

    def connect_dos(self, dos):
        for do in dos:
            channel = grpc.insecure_channel(f'{do.addr}:{do.port}')
            self.stub[do.name] = fedpred_pb2_grpc.FedPredStub(channel)
            for attr in do.data.keys():
                self.ka_map[attr] = do.name

    def query(self, x):
        now = self.model
        while not hasattr(now, 'pos'):
            doi = self.ka_map[now.ka]
            msg = {
                'uid': x,
                'ka': now.ka,
                'kv': now.kv,
            }
            msg = pickle.dumps(msg)
            res = self.stub[doi].enc_msg(fedpred_pb2.EncMsg(action='query', ct=msg))
            res = pickle.loads(res.ct)
            if res:
                now = now.lc
            else:
                now = now.rc
        return now.pos
