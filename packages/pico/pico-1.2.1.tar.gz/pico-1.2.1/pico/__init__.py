"""
Pico is a very small RPC library and web application framework for Python.

Copyright (c) 2012, Fergal Walsh.
License: BSD
"""

__author__ = 'Fergal Walsh'
__version__ = '1.2.1'

import json
import os
import decimal
import datetime

path = (os.path.dirname(__file__) or '.') + '/'

def cacheable(func):
    func.cacheable = True
    return func

def stream(func):
    func.stream = True
    return func

def private(func):
    func.private = True
    return func

def protected(users=None, groups=None):
    def decorator(func):
        func.protected = True
        func.protected_users = users
        func.protected_groups = groups
        return func
    if callable(users):
        f = users
        users = None
        groups = None
        return decorator(f)
    if users and not hasattr(users, '__iter__'):
        users = [groups]
    if groups and not hasattr(groups, '__iter__'):
        groups = [groups]
    return decorator


class Pico(object):
    def __init__(self):
        pass
    
class object(object):
    def __init__(self, **kwargs):
        self.__dict__.update(kwargs)

    @property
    def json(self):
        return to_json(self.__dict__)

    def __str__(self):
        return self.json
    

class JSONString(str):
    def __init__(self, s):
        pass

def convert_keys(obj):
    if type(obj) == dict: # convert non string keys to strings
        return dict((str(k), convert_keys(obj[k])) for k in obj)
    else:
        return obj


def to_json(obj, _json_dumpers = {}):
    if isinstance(obj, JSONString):
        return obj
    class Encoder(json.JSONEncoder):
        def default(self, obj):
            if type(obj) in _json_dumpers:
                obj = _json_dumpers[type(obj)](obj)
                convert_keys(obj)
                return obj
            for obj_type, dumper in _json_dumpers.iteritems():
                if isinstance(obj, obj_type):
                    return dumper(obj)
            if hasattr(obj, 'as_json'):
                return obj.as_json()
            if hasattr(obj, 'json'):
                return json.loads(obj.json)
            elif hasattr(obj, 'tolist'):
                return obj.tolist()
            elif hasattr(obj, 'read') and hasattr(obj, 'seek'):
                s = obj.read()
                obj.close()
                return s
            elif hasattr(obj, '__iter__'):
                return list(obj)
            else:
                return str(obj)
    
        def encode(self, obj):
            convert_keys(obj)
            return json.JSONEncoder.encode(self, obj)
    for k in json_dumpers:
        if k not in _json_dumpers:
            _json_dumpers[k] = json_dumpers[k]
    obj = convert_keys(obj)
    s = json.dumps(obj, cls=Encoder, separators=(',',':'))
    return s

def from_json(v, _json_loaders = []):
    if isinstance(v, basestring):
        _json_loaders.extend(json_loaders)
        for f in _json_loaders:
            try:
                v = f(v)
                break
            except Exception, e:
                continue
    return v


json_dumpers = {
    decimal.Decimal: lambda d: float(d)
}

json_loaders = [
lambda s: datetime.datetime.strptime(s, '%Y-%m-%d %H:%M:%S')
]

magic = 'hjksdfjgg;jfgfdggldfgj' # used in the check to see if a module has explicitly imported Pico to make it Picoable
STREAMING = False
