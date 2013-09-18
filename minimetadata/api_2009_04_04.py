#!/usr/bin/python

import os
import sys
import argparse
import pprint

import bottle
import pystache

from .mddict import MDDict
from . import utils

app = bottle.Bottle()
metadata = MDDict()
userdata = None

def value_or_file(v):
    '''If v starts with @, interpret the remainder of the string as a
    filename and return the contents of that file.  Otherwise return the
    raw value of v.'''

    if v.startswith('@'):
        with open(os.path.expanduser(v[1:])) as fd:
            v = fd.read()

    ctx = {}
    if bottle.request.remote_addr is not None:
        ctx['client_ip'] = bottle.request.remote_addr
        ctx['client_ip_as_hex'] = '{:0X}'.format(utils.ip2long(bottle.request.remote_addr))

    return pystache.render(v, ctx)

@app.route('/meta-data/')
def get_metadata_index():
    return get_metadata_value('/')

@app.route('/meta-data/<key:path>', name='meta-data')
def get_metadata_value(key):
    bottle.response.content_type = 'text/plain'

    try:
        if key.endswith('/'):
            orig_key = key
            key = key[:-1]
        else:
            orig_key = key

        v = metadata.lookup(key)

        if orig_key.endswith('/'):
            # If the client requested a container, return a list of keys
            # if it's a dictionary or a 404 error otherwise.
            if isinstance(v, dict):
                if all(x.isdigit() for x in v.keys()):
                    # This is a hack primarily for meta-data/public-keys, but
                    # generalized for any other container with integer keys,
                    # assuming that the labels in the generated listing
                    # aren't important.
                    return '\n'.join('{}=item{}'.format(x,x) for x in
                            v.keys())
                else:
                    # Returns a listing of subkeys in the container,
                    # appending '/' for things that contain additional
                    # subkeys.
                    return '\n'.join('{}/'.format(x)
                            if isinstance(v[x], dict)
                            else x for x in v.keys())
            else:
                raise KeyError(orig_key)
        else:
            if isinstance(v, dict):
                # If the item they requested is a container, redirect
                # with a trailing '/'.
                bottle.redirect(
                        app.get_url('meta-data', key=orig_key + '/'))
        
            # Return the value of the requested key.
            return value_or_file(v)
    except KeyError as detail:
        bottle.abort(404, 'Failed to find {:s}'.format(detail))

@app.route('/user-data/')
def get_userdata():
    if userdata is None:
        bottle.abort(404)

    return userdata

def setup(cfg):
    global metadata
    global userdata

    metadata.parse(cfg.get('meta-data', {}))
    metadata.close()

    if 'user-data' in cfg:
        userdata = value_or_file(cfg['user-data'])

