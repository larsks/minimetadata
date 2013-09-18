#!/usr/bin/python

import os
import sys
import argparse
import pprint

import bottle

from .mddict import MDDict

app = bottle.Bottle()
metadata = MDDict()
userdata = None

def value_or_file(v):
    if v.startswith('@'):
        with open(v[1:]) as fd:
            v = fd.read()

    return v

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
    except KeyError:
        bottle.abort(404)

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

