import os
import sys
import argparse
import yaml

import bottle
from bottle import Bottle, run

from . import api_2009_04_04

app = Bottle()

@app.route('/')
def index():
    return '\n'.join(['2009-04-04'])

def setup(cfgpath):
    with open(cfgpath) as fd:
        cfg = yaml.load(fd)

    api_2009_04_04.setup(cfg)
    app.mount('/2009-04-04/', api_2009_04_04.app)
    app.mount('/latest/',     api_2009_04_04.app)

def parse_args():
    p = argparse.ArgumentParser()
    p.add_argument('--config', '-f',
            default='metadata.yaml')
    p.add_argument('--port', '-p', default=8775, type=int)
    p.add_argument('--bind', '-b', default='0.0.0.0')

    return p.parse_args()

def main():
    global cfg

    opts = parse_args()
    setup(opts.config)
    run(app, host=opts.bind, port=opts.port)

if __name__ == '__main__':
    main()

