from __init__ import ProxyFactory
from models import Proxy
from multiprocessing import Pool

import getopt
import os, sys
import logging

logger = logging.getLogger('hallucination')
logger.addHandler(logging.StreamHandler(sys.stdout))
logger.setLevel(logging.INFO)

config = {}

# FIXME: This is not a good design
url = 'http://translator.suminb.com'
proxy_factory = None


def testrun_request(proxy):
    # NOTE: For some reason, testrun_worker has problems of calling class-level
    # functions. It will produce an error message like following:
    # PicklingError: Can't pickle <type 'function'>: attribute lookup __builtin__.function failed
    proxy_factory.make_request(url, proxy=proxy)

def testrun_worker(proxy):
    try:
        logger.info('Test run: Fetching %s via %s' % (url, proxy))
        testrun_request(proxy)
    except Exception as e:
        logger.error(str(e))

def testrun():
    pool = Pool(processes=8)
    pool.map(testrun_worker, proxy_factory.session.query(Proxy).all())


def _import(params):
    """Imports a list of proxy servers from a text file."""
    proxy_factory.import_proxies(params)


def export():
    """Exports the list of proxy servers to the standard output."""
    pass


def select():
    print proxy_factory.select(1)


def main():
    opts, args = getopt.getopt(sys.argv[1:], 'ti:x:sd:')

    rf = None
    params = []
    for o, a in opts:
        if o == '-t':
            rf = testrun
        elif o == '-i':
            rf = _import
            params = [a]
        elif o == '-x':
            rf = export
        elif o == '-s':
            rf = select

        elif o == '-d':
            config['db_uri'] = 'sqlite:///%s' % a

            global proxy_factory
            proxy_factory = ProxyFactory(config=dict(db_uri=config['db_uri']))

    if rf != None:
        rf(*params)
    else:
        raise Exception('Runtime mode is not specified.')

if __name__ == '__main__':
    main()
