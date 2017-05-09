import json
import serial
import _thread

from autobahn.asyncio.websocket import WebSocketServerProtocol, \
    WebSocketServerFactory

ser = serial.Serial('/dev/ttyACM0', 115200, timeout=0.04)

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


def getData(_self, isBinary):
    """

    :return:
    """
    while True:
        try:
            print(ser.readline().decode('utf-8')[:-5].split(','))
            arr = ser.readline().decode('utf-8')[:-5].split(',')
            arr_n = []
            i = 0
            while i < 4:
                arr_n.append(float(arr[i]))
                i += 1
            _self.sendJSONmsg(str({"data": arr_n}), isBinary)
        except Exception as ex:
            print('error receive data - %s', ser.readline().decode('utf-8'))
            print('%s', ex)

if __name__ == '__main__':

    try:
        import asyncio
    except ImportError:
        # Trollius >= 0.3 was renamed
        # import trollius as asyncio
        print('import asyncio failed')

    factory = WebSocketServerFactory("ws://localhost:6544")
    factory.protocol = MyServerProtocol

    loop = asyncio.get_event_loop()
    coro = loop.create_server(factory, 'localhost', 6544)
    server = loop.run_until_complete(coro)

    try:
        loop.run_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.close()
        loop.close()
