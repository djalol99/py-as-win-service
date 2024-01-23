from simple_websocket_server import WebSocketServer, WebSocket
from serial import Serial, SerialException
import sys
import json


class ScaleWebSocket(WebSocket):
    protocol = "A9"
    _reset = True
    ws_server = None

    def handle(self):
        try:
            data = json.loads(self.data)
            cmd = data['cmd']
            if cmd == 'start':
                self.connect_to_scale(data['comport']) # comport example: "COM8"
                self.send_data()
            elif cmd == 'resume':
                self.update_connection_to_scale()
                self.send_data()
            elif cmd == 'stop':
                self.close_connection_to_scale()
            else:
                self.send_data()    
        except:
            self.send_error("Something went wrong. Please, check the message which you are sending")

    def connected(self):
        pass

    def handle_close(self):
        pass

    # custom methods
    def send_data(self):
        if self.ws_server.serial_conn and self.ws_server.serial_conn.is_open:
            self.read_data_from_scale()
            self.send_message(json.dumps({
                "ok": True,
                "data": self._weight
            }))
        else:
            self.send_error()

    def send_error(self, message=None):
        if message is None:
            message = "Something went wrong. Please, check connection with scales."
        self.send_message(json.dumps({
            "ok": False,
            "message": message
        }))

    def update_connection_to_scale(self):
        try:
            if self.ws_server.serial_conn and not self.ws_server.serial_conn.is_open:
                self.ws_server.serial_conn.open()
        except SerialException as ex:
            self.send_error("Cannot resume connection")

    def close_connection_to_scale(self):
        if self.ws_server.serial_conn:
            self.ws_server.serial_conn.close()
        self.send_message(json.dumps({
                "ok": True,
                "data": 0
            }))

    def connect_to_scale(self, comport=None):
        if comport is None:
            return
        try:
            if self.ws_server.serial_conn and self.ws_server.serial_conn.is_open:
                self.ws_server.serial_conn.close()
            self.ws_server.serial_conn = Serial(comport)
            self.read_data_from_scale()

            self.send_data()
        except SerialException as ex:
            self.close()

    def read_data_from_scale(self):
        try:
            if self._reset:
                self.ws_server.serial_conn.reset_input_buffer()

            SOF = "02"
            EOF = "03"
            # FIND START OF FRAME
            while self.ws_server.serial_conn.read().hex() != SOF:
                continue
            # RECORD UNTIL END OF FRAME
            data = bytes()
            while True:
                temp = self.ws_server.serial_conn.read()
                if temp.hex() == EOF:
                    break
                else:
                    data += temp
            self._weight = self.get_weight(data.decode("utf-8"))
        except SerialException:
            self.ws_server.serial_conn.is_open = False
            self.send_error()

    def get_weight(self, data):
        try:
            if self.protocol == "A9":
                decimal = int(data[7])
                return str(round(int(data[:7]) * 10**(-decimal), decimal))
            else:
                return data
        except:
            return "0"


def start_server(host="127.0.0.1", port=None):
    if host and port and comport and protocol:
        ScaleWebSocket.comport = comport
        ScaleWebSocket.protocol = protocol
        try:
            server = get_ws_server(host, port)
            server.serve_forever()
        except OSError:
            pass

def get_ws_server(host="127.0.0.1", port=None):
    WebSocketServer.serial_conn = None
    server = WebSocketServer(host, port, ScaleWebSocket)
    ScaleWebSocket.ws_server = server
    return server


if __name__ == "__main__":
    host = '127.0.0.1'
    port = 7001
    comport = 'COM8'
    protocol = 'A9'
    for param in sys.argv:
        key_val = param.split("=")
        if key_val[0] == "host":
            host = key_val[1]
        elif key_val[0] == "port":
            port = key_val[1]
        elif key_val[0] == "comport":
            comport = key_val[1]
        elif key_val[0] == "protocol":
            protocol = protocol

    start_server(host=host, port=port, comport=comport, protocol=protocol)