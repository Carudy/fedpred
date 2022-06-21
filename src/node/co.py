import pickle
import random
import sys
from phe import paillier

# import grpc

from ..alg import *
# from ..proto import *


class Coodinator:
    def __init__(self):
        self.sign_key, self.verify_key = gen_sign_key()
        self.model = None
        self.ka_map = {}
        self.stub = {}
        self.phe_pk, self.phe_sk = paillier.generate_paillier_keypair()

    def receive_model(self, model):
        self.model = pickle.loads(model)

    def connect_dos(self, dos):
        for do in dos:
            # channel = grpc.insecure_channel(f'{do.addr}:{do.port}')
            # self.stub[do.name] = fedpred_pb2_grpc.FedPredStub(channel)
            for attr in do.data.keys():
                self.ka_map[attr] = do.name

    def query(self, x, comm_arr=None):
        now = self.model
        opf = True

        while now.lc:
            doi = self.ka_map[now.ka]
            r = str(random.random()).encode()
            ct = self.mo.enc_box[doi].encrypt(r)
            param = int.from_bytes(ct, "big")
            if param < 2 ** 12:
                logger.warning('Ct too small.')
            v0 = self.dos[doi].data[now.ka][x]
            v1 = self.mo.node_map[now.pos].kv
            if opf:
                opf = get_ope(param)
                c0 = opf(v0)
                c1 = opf(v1)
                if comm_arr is not None:
                    ov = sys.getsizeof(c0) + sys.getsizeof(c1) + sys.getsizeof(ct)
                    comm_arr[-1] += ov
            else:
                c0, c1 = self.phe_pk.encrypt(float(v0)), self.phe_pk.encrypt(float(v1))
                df = c0 - c1
                noise = random.randint(123456, 789012)
                df = df * (1. / noise)
                df = self.phe_sk.decrypt(df)
                if comm_arr is not None:
                    ov = sys.getsizeof(c0) + sys.getsizeof(df)
                    comm_arr[-1] += ov
            if opf:
                if (v0 - v1) * (c0 - c1) <= 0 and v0 != v1:
                    logger.warning('OPE failed!')
                    print(v0, v1, c0, c1, param, opf.a, opf.b, opf.c)
            if (opf and c0 <= c1) or (opf==False and df <= 0):
                now = now.lc
            else:
                now = now.rc
        return now.pos
