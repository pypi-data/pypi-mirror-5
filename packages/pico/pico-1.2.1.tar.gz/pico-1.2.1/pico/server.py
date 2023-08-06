from wsgiref.util import setup_testing_defaults
import wsgiref.simple_server

import sys
import cgi
import json
import inspect
import os
import mimetypes
import urlparse
import hashlib
import decimal
import traceback
import getopt
import re
import datetime
import time

import wsgiref
import SocketServer
import threading

import pico
import pico.modules

pico_path = (os.path.dirname(__file__) or '.') + '/'
_server_process = None
pico_exports = []

class Response(object):
    def __init__(self, **kwds):
        self.status = '200 OK'
        self._headers = {}
        self.type = "object"
        self.cacheable = False
        self.callback = None
        self.json_dumpers = {}
        self.__dict__.update(kwds)
    
    def __getattribute__(self, a):
        try:
            return object.__getattribute__(self, a)
        except AttributeError, e:
            return None

    def set_header(self, key, value):
        self._headers[key] = value

    @property   
    def headers(self):
        headers = dict(self._headers)
        if self.cacheable:
            headers['Cache-Control'] = 'public, max-age=22222222'
        if self.type == 'stream':
            headers['Content-Type'] = 'text/event-stream'
        elif self.type == 'object':
            if self.callback:
                headers['Content-Type'] = 'application/javascript'
            else:
                headers['Content-Type'] = 'application/json'
            headers['Content-Length'] = str(len(self.output[0]))
        else:
            if 'Content-type' not in headers:
                headers['Content-Type'] = 'text/plain'
        return headers.items()


    @property
    def output(self):
        if self._output:
            return self._output
        log(self.type)
        if hasattr(self.content, 'read') and hasattr(self.content, 'seek') and hasattr(self.content, 'close'):
            self.type = "file" # it looks like a duck... a file
        if self.type == "plaintext":
            return [self.content,]
        if self.type == "file":
            return self.content
        if self.type == "stream":
            def f(stream):
                for d in stream:
                    yield 'data: ' + pico.to_json(d) + '\n\n'
                yield 'data: "PICO_CLOSE_STREAM"\n\n'
            return f(self.content)
        if self.type == "chunks":
            log("chunks")
            def f(response):
                yield (' ' * 1200) + '\n'
                yield '[\n'
                delimeter = ''
                for r in response:
                    yield delimeter + pico.to_json(r, self.json_dumpers) + '\n'
                    delimeter = ','
                yield "]\n"
            return f(self.content)
        else:
            s = pico.to_json(self.content, self.json_dumpers)
            if self.callback:
                s = self.callback + '(' + s + ')'
            s = [s,]
            self._output = s
            return s

class APIError(Exception): pass

def main():
    opts_args = getopt.getopt(sys.argv[1:], "hp:dm", ["help", "port=", "no-reload"])
    args = dict(opts_args[0])
    port = int(args.get('--port', args.get('-p', 8800)))
    multithreaded = '-m' in args
    global RELOAD
    RELOAD = RELOAD and ('--no-reload' not in args)
    host = '0.0.0.0' #'localhost'
    server = make_server(host, port, multithreaded)
    print("Serving on http://localhost:%s/"%port)
    print("Using %s."%('multiple threads' if multithreaded else 'a single thread'))
    print("URL map: ")
    print('\t' + '\n\t'.join(["%s : %s "%(url, path) for url, path in STATIC_URL_MAP]))
    print("Hit CTRL-C to end")
    server.serve_forever()


def make_server(host='0.0.0.0', port=8800, multithreaded=False):
    if multithreaded:
        class ThreadedTCPServer(SocketServer.ForkingMixIn, wsgiref.simple_server.WSGIServer):
            pass
        server = ThreadedTCPServer((host, port), wsgiref.simple_server.WSGIRequestHandler)
        server.set_app(wsgi_dev_app)
    else:
        server = wsgiref.simple_server.make_server(host, port, wsgi_dev_app)
    def log_message(self, format, *args):
        if not SILENT:
            print(format%(args))
    server.RequestHandlerClass.log_message = log_message
    return server

def start_thread(host='127.0.0.1', port=8800, silent=True):
    global RELOAD, SILENT, _server_process
    RELOAD = False
    SILENT = silent
    class Server(threading.Thread):
        def __init__(self):
            super(Server, self).__init__()
            self._server = make_server(host, port)

        def run(self):
            self._server.serve_forever()

        def stop(self):
            self._server.shutdown()
            self._server.socket.close()
            print("Pico server has stopped")

    _server_process = Server()
    _server_process.start()
    print("Serving on http://%s:%s/"%(host, port))
    return _server_process

def stop_thread():
    _server_process.stop()
    _server_process.join(1)


def is_authorised(f, authenticated_user):
    if hasattr(f, 'private') and f.private:
        return False
    if getattr(f, 'protected', False):
        if (authenticated_user == None):
            return False
        else:
            if f.protected_users == None and f.protected_groups == None:
                return True
            if f.protected_users and authenticated_user in f.protected_users:
                return True
            if f.protected_groups and set(USERS.get(authenticated_user)['groups']).intersection(f.protected_groups):
                return True
            return False
    else:
        return True
    return False

def call_function(module, function_name, parameters, authenticated_user=None):
    try:
        f = getattr(module, function_name)
    except Exception:
        raise Exception("No matching function availble. You asked for %s with these parameters %s!"%(function_name, parameters))
    if not is_authorised(f, authenticated_user):
        raise Exception("You are not authorised to access this function")
    if 'pico_user' in f.func_code.co_varnames:
        parameters.update({'pico_user': authenticated_user})
    results = f(**parameters)
    response = Response(content=results)
    if hasattr(f, 'cacheable') and f.cacheable:
        response.cacheable = True
    if hasattr(f, 'stream') and f.stream and STREAMING:
        response.type = "stream"
    elif response.content.__class__.__name__ == 'generator':
        response.type = "chunks"
    return response
    

def call_method(module, class_name, method_name, parameters, init_args, authenticated_user=None):
    try:
        obj = getattr(module, class_name)(*init_args)
    except KeyError, e:
        raise Exception("No matching class availble. You asked for %s!"%(class_name))
    r = call_function(obj, method_name, parameters, authenticated_user)
    del obj
    return r 

def cache_key(params):
    params = dict(params)
    if '_callback' in params:
        del params['_callback']
    hashstring = hashlib.md5(str(params)).hexdigest()
    cache_key = "__".join([params.get('_module', ''), params.get('_class', ''), params.get('_function', ''), hashstring])
    return cache_key.replace('.', '_')


def call(params):
    function = params.get('_function', '')
    module_name = params.get('_module', '')
    parameters = dict(params)
    for k in parameters.keys():
        if k.startswith('_') or k.startswith('pico_'):
            del parameters[k]
        else:
            try:
                parameters[k] = json.loads(parameters[k])
            except Exception:
                try:
                    parameters[k] = json.loads(parameters[k].replace("'", '"'))
                except Exception:
                    parameters[k] = parameters[k]
    callback = params.get('_callback', None)
    init_args = json.loads(params.get('_init', '[]'))
    class_name = params.get('_class', None)
    usecache = json.loads(params.get('_usecache', 'true'))
    response = Response()
    if module_name == 'pico':
        if function == 'authenticate':
            response.content = authenticate(params)
    elif usecache and os.path.exists(CACHE_PATH):
        try:
            response = serve_file(CACHE_PATH + cache_key(params))
            log("Serving from cache")
        except OSError:
            pass
    if not response.content:
        module = pico.modules.load(module_name, RELOAD)
        authenticated_user = authenticate(params, module)
        for k in parameters:
            parameters[k] = pico.from_json(parameters[k], getattr(module, "json_loaders", []))
        if class_name:
            init_args = map(lambda s: pico.from_json(s, getattr(module, "json_loaders", [])), init_args)
            response = call_method(module, class_name, function, parameters, init_args)
        else:
            response = call_function(module, function, parameters, authenticated_user)
        response.json_dumpers = getattr(module, "json_dumpers", {})
        log(usecache, response.cacheable)
        if usecache and response.cacheable:
            log("Saving to cache")
            try:
                os.stat(CACHE_PATH)
            except Exception:
                os.mkdir(CACHE_PATH)
            f = open(CACHE_PATH + cache_key(params) + '.json', 'w')
            out = response.output
            if hasattr(out, 'read'):
                out = out.read()
                response.output.seek(0)
            else:
                out = out[0]
            f.write(out)
            f.close()
    response.callback = callback
    return response

def _load(module_name, params={}):
    params['_module'] = 'pico.modules'
    params['_function'] = 'load'
    params['module_name'] = '"%s"'%module_name
    return call(params)

def serve_file(file_path):
    response = Response()
    size = os.path.getsize(file_path)
    mimetype = mimetypes.guess_type(file_path)
    response.set_header("Content-type", mimetype[0] or 'text/plain')  
    response.set_header("Content-length", str(size))
    response.set_header("Cache-Control", 'public, max-age=22222222')
    response.content = open(file_path, 'rb')
    response.type = "file"
    return response


def static_file_handler(path):
    file_path = ''
    for (url, directory) in STATIC_URL_MAP:
        m = re.match(url, path)
        if m:
            file_path = directory + ''.join(m.groups())

    # if the path does not point to a valid file, try default file 
    file_exists = os.path.isfile(file_path)
    if not file_exists:
        file_path = os.path.join(file_path, DEFAULT)
    return serve_file(file_path)
    

def _hash(s):
    m = hashlib.md5()
    m.update(s)
    return m.hexdigest()
    
def authenticate(params, module=None):
    users = USERS
    if users == {} or users == None:
        if module and hasattr(module, 'PICO_USERS'):
            users = module.PICO_USERS
        else:
            return None
    username = params.get('_username', None)
    if username:
        key = params.get('_key', '')
        nonce = params.get('_nonce', '')
        dt =  time.time() - int(nonce)
        if dt > 60:
            raise Exception("Bad nonce. The time difference is: %s"%dt)
        password = users.get(username, {}).get('password', None)
        # log(password, str(nonce), _hash(password + str(nonce)))
        if password and key == _hash(password + str(nonce)):
            log("authenticated_user: %s"%username)
        else:
            raise Exception("Bad username or password")
        return username
    else:
        return None

def log(*args):
    if not SILENT:
        print(args[0] if len(args) == 1 else args)

def extract_params(environ):
    params = {}
    # if parameters are in the URL, we extract them first
    get_params = environ['QUERY_STRING']
    if get_params == '' and '/call/' in environ['PATH_INFO']:
        path = environ['PATH_INFO'].split('/')
        environ['PATH_INFO'] = '/'.join(path[:-1]) + '/'
        params.update(cgi.parse_qs(path[-1]))

    # now get GET and POST data
    fields = cgi.FieldStorage(fp=environ['wsgi.input'], environ=environ)
    for name in fields:
        if fields[name].filename:
            params[name] = fields[name].file
        elif type(fields[name]) == list and fields[name][0].file:
            params[name] = [v.file for v in fields[name]]
        else:
            params[name] = fields[name].value
    return params

def generate_exception_report(e, path, params):
    response = Response()
    full_tb = traceback.extract_tb(sys.exc_info()[2])
    tb_str = ''
    for tb in full_tb:
        tb_str += "File '%s', line %s, in %s; "%(tb[0], tb[1], tb[2])
    report = {}
    report['exception'] = str(e)
    report['traceback'] = tb_str
    report['url'] = path.replace('/pico/', '/')
    report['params'] = dict([(k, repr(params[k])[:100] + ('...' if len(repr(params[k])) > 100 else '')) for k in params])
    log(json.dumps(report, indent=1))
    response.content = report
    response.status = '500 ' + str(e)
    return response


def handle_api_v1(path, params):
    if '/module/' in path:
        module_name = path.split('/')[2]
        return _load(module_name, params)
    elif '/call/' in path:
        return call(params)
    elif '/authenticate/' in path:
        return authenticate(params)
    raise APIError()

def handle_api_v2(path, params):
    # nice urls:
    #   /module_name/
    #   /module_name/function_name/?foo=bar
    #   /module_name/function_name/foo=bar # not implemented!
    #   /module_name/class_name/function_name/
    parts = [p for p in path.split('/') if p]
    if len(parts) == 1:
        return _load(parts[0], params)
    elif len(parts) == 2:
        params['_module'] = parts[0]
        params['_function'] = parts[1]
        return call(params)
    elif len(parts) == 3:
        params['_module'] = parts[0]
        params['_class'] = parts[1]
        params['_function'] = parts[2]
        return call(params)
    raise APIError(path)

def handle_pico_js(path, params):
    if path == '/pico.js' or path == '/client.js':
        return serve_file(pico_path + 'client.js')
    raise APIError()

def not_found_error(path):
    response = Response()
    response.status = '404 NOT FOUND'
    response.content = '404 File not found'
    response.type = 'plaintext'
    return response

def wsgi_app(environ, start_response, enable_static=False):
    setup_testing_defaults(environ)
    if environ['REQUEST_METHOD'] == 'OPTIONS':
        # This is to hanle the preflight request for CORS.
        # See https://developer.mozilla.org/en/http_access_control
        response = Response()
        response.status = "200 OK"
    else:
        params = extract_params(environ)
        log('------')
        path = environ['PATH_INFO'].split(environ['HTTP_HOST'])[-1]
        if BASE_PATH: path = path.split(BASE_PATH)[1]
        log(path)
        try:
            if '/pico/' in path:
                path = path.replace('/pico/', '/')
                try:
                    response = handle_api_v1(path, params)
                except APIError:
                    try:
                        response = handle_pico_js(path, params)
                    except APIError:
                        try:
                            response = handle_api_v2(path, params)
                        except APIError:
                            response = not_found_error(path)
            elif enable_static:           
                try:
                    response = static_file_handler(path)
                except OSError, e:
                    response = not_found_error(path)
            else:
                response = not_found_error(path)
        except Exception, e:
            response = generate_exception_report(e, path, params)
    response.set_header('Access-Control-Allow-Origin', '*')
    response.set_header('Access-Control-Allow-Headers', 'Content-Type')
    response.set_header('Access-Control-Expose-Headers', 'Transfer-Encoding')
    start_response(response.status, response.headers)
    return response.output


def wsgi_dev_app(environ, start_response):
    return wsgi_app(environ, start_response, enable_static=True)


CACHE_PATH = './cache/'
BASE_PATH = ''
STATIC_URL_MAP = [
('^/(.*)$', './'),
]
DEFAULT = 'index.html'
RELOAD = True
STREAMING = False
SILENT = False
USERS = {}
if __name__ == '__main__':
    main()
