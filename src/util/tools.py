import importlib
import sys
import time

from .log import *


def start_and_join(threads):
    for td in threads:
        td.start()
    for td in threads:
        td.join()


def import_from_file(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


def wait_func(func, t=0.2, in_runtime=True):
    """
        A "wait_func" will repeatly run until it returns True.
        Notice the return type of func must be bool.
    """

    def decor(*args, **kwargs):
        res = None
        while res is not True:
            try:
                if in_runtime and args[0].stopped():
                    return
                res = func(*args, **kwargs)
            except Exception as e:
                logger.info('Exception happend in a wait_func.')
                logger.info(e)
                return
            else:
                time.sleep(t)
        return res

    return decor
