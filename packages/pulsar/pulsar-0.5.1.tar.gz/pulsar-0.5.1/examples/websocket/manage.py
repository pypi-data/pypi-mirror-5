'''\
A very Simple Web-Socket example.
To run the server type::

    python manage.py
    
and open a web browser at http://localhost:8060    
'''
import os
import sys
import json
from random import random
import time
try:
    import pulsar
except ImportError: #pragma nocover
    sys.path.append('../../')
    import pulsar
from pulsar.apps import ws, wsgi
from pulsar.utils.httpurl import range


class Graph(ws.WS):
    
    def on_message(self, request, msg):
        return json.dumps([(i,random()) for i in range(100)])

    
class Echo(ws.WS):
    
    def on_message(self, request, msg):
        return msg


class Site(wsgi.LazyWsgi):
    
    def setup(self):
        return wsgi.WsgiHandler([wsgi.Router('/', get=self.home),
                                 ws.WebSocket('/data', Graph()),
                                 ws.WebSocket('/echo', Echo())])
    
    def home(self, request):
        data = open(os.path.join(os.path.dirname(__file__), 
                     'websocket.html')).read()
        data = data % request.environ
        request.response.content_type = 'text/html'
        request.response.content = data
        return request.response.start()


def server(**kwargs):
    return wsgi.WSGIServer(callable=Site(), **kwargs)


if __name__ == '__main__':  #pragma nocover
    server().start()
