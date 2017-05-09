import json
import serial
import _thread

from autobahn.asyncio.websocket import WebSocketServerProtocol, \
    WebSocketServerFactory

import tornado.ioloop
import tornado.web
import tornado.websocket

from tornado.options import define, options, parse_command_line

ser = serial.Serial('/dev/ttyACM0', 115200, timeout=0.04)
define("port", default=8888, help="run on the given port", type=int)
# we gonna store clients in dictionary..
clients = dict()


class IndexHandler(tornado.web.RequestHandler):
    @tornado.web.asynchronous
    def get(self):
        self.write("This is your response")
        self.finish()


class WebSocketHandler(tornado.websocket.WebSocketHandler):
    def open(self, *args):
        self.id = self.get_argument("Id")
        self.stream.set_nodelay(True)
        clients[self.id] = {"id": self.id, "object": self}
        print("WebSocket connection open.")

    def on_message(self, message):
        """
        when we receive some message we want some message handler..
        for this example i will just print message to console
        """
        if type(message) == str:
            print("Binary Message recieved")
            #Echo the binary message back to where it came from
            #self.write_message(message, binary=True)
        else:
            print(message)
            #Send back a simple "OK"
            #self.write_message('ok')
        #message = json.loads(payload.decode('utf8'))   # message - python string, payload - utf8 encoded json string
        words = message.split(" ")
        if words[0] == 'get_data':
            _thread.start_new_thread(getData, (self))

        if words[0] == 'send_data':
            print('send_data')
            try:
                count = int(words[1])
                if count > 0 and count < 100:
                    s = '{:03d}r;'.format(count)
                    ser.write(bytes(s, 'utf-8'))
            except Exception as ex:
                print("error send - {0}".format(message))

    def on_close(self):
        if self.id in clients:
            del clients[self.id]

app = tornado.web.Application([
    (r'/', IndexHandler),
    (r'/', WebSocketHandler),
])

if __name__ == '__main__':
    parse_command_line()
    app.listen(options.port)
    tornado.ioloop.IOLoop.instance().start()

"""
class MyServerProtocol(WebSocketServerProtocol):

    def onConnect(self, request):
        print(self.peer, 'connected')

    def onOpen(self):
        print("WebSocket connection open.")

    def onMessage(self, payload, isBinary):
        if isBinary:
            print("Binary message received: {0} bytes".format(len(payload)))
        else:
            print("Text message received: {0}".format(payload.decode('utf8')))
        message = json.loads(payload.decode('utf8'))   # message - python string, payload - utf8 encoded json string
        words = message.split(" ")
        if words[0] == 'get_data':
            _thread.start_new_thread(getData, (self, isBinary))

        if words[0] == 'send_data':
            print('send_data')
            try:
                count = int(words[1])
                if count > 0 and count < 100:
                    s = '{:03d}r;'.format(count)
                    ser.write(bytes(s, 'utf-8'))
            except Exception as ex:
                print("error send - {0}".format(message))


    def onClose(self, wasClean, code, reason):
        print("WebSocket connection closed: {0}".format(reason))

    def sendJSONmsg(self, message, isBinary):
        self.sendMessage(message.encode('utf-8'), isBinary)
"""

def getData(_self):
    """

    :return:
    """
    while True:
        try:
            print(ser.readline().decode('utf-8')[:-5].split(','))
            _self.write_message(str({"data": list(map(int, ser.readline().decode('utf-8')[:-5].split(',')))}))
        except Exception as ex:
            print('error receive data - %s', ser.readline().decode('utf-8'))

