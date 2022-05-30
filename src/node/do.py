import pickle
import random
from concurrent import futures
import grpc

from ..alg import *
from ..proto import *


class GrpcService(fedpred_pb2_grpc.FedPred):
    def __init__(self, do):
        self.do = do

    def keyex(self, request, context):
        if not verify_sign(request.sign.pk, request.sign.ct, request.sign.msg):
            logger.info('Sign failed.')
            return fedpred_pb2.HelloRes(r=0)
        logger.info('Sign checked.')
        self.do.mo_s = str(request.r).encode()
        self.do.get_box()
        logger.info('Sym_box generated.')
        return fedpred_pb2.HelloRes(r=self.do.secret)

    def enc_msg(self, request, context):
        msg = self.do.mo_box.decrypt(request.ct)
        if request.action == 'range':
            ranges = pickle.loads(msg)
            logger.info('Received margins.')
            print(ranges)
        return fedpred_pb2.EncMsg(action='range', ct=b'ok')


class DataOwner:
    def __init__(self, co, attrs, name):
        self.co = co
        self.data = None
        self.attrs = attrs
        self.name = name
        self.secret = random.choice(range(1000))

        self.rpc_service = GrpcService(self)
        self.rpc_server = grpc.server(futures.ThreadPoolExecutor(max_workers=2))
        fedpred_pb2_grpc.add_FedPredServicer_to_server(self.rpc_service, self.rpc_server)
        self.port = int(self.name) + 50000
        self.addr = 'localhost'
        self.rpc_server.add_insecure_port(f'[::]:{self.port}')
        self.rpc_server.start()

    def get_box(self):
        self.mo_box = kdf_box(self.mo_s, str(self.secret).encode())
