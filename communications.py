import json
import socket

import numpy as np

_col_dict = {0: 'A', 1: 'B', 2: 'C', 3: 'D', 4: 'E', 5: 'F', 6: 'G', 7: 'H', 8: 'I'}


class CommunicationsHandler:
    def __init__(self, name, ip, color, timeout):
        color = color.lower()
        if color not in ('w', 'b'):
            raise ValueError("Role {} not defined".format(color))

        # Initialization
        self.role = color
        self.port = 5800 if color == 'w' else 5801
        self.name = name
        self.ip = ip
        self.timeout = timeout

        # Establish connection with server
        try:
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket.connect((self.ip, self.port))
        except socket.error as e:
            print("Connection error: {}".format(e))

    def _send_string(self, string: str):
        try:
            _bytes = len(string).to_bytes(4, byteorder='big')
            _bytes += string.encode('utf-8')
            self.socket.send(_bytes)
            print("Bytes sent: ", _bytes, "\n")
        except socket.error as err:
            print('Send failed! Error Code : ', format(err))

    def send_name(self):
        self._send_string(self.name)

    def listen_state(self):
        while 1:
            data = self.socket.recv(4096)
            if len(data) > 4:
                data_string = data.decode(encoding='utf-8', errors='replace')
                data_string = data_string[data_string.find('{'):]
                json_data = json.loads(data_string)
                decoded_state = self._decode_json_board(json_data['board'])
                decoded_turn = 'w' if json_data['turn'] == 'WHITE' else 'b'
                return decoded_state, decoded_turn

    def send_move(self, origin: tuple, destination: tuple):
        orig = _col_dict[origin[1]] + str(origin[0] + 1)
        dest = _col_dict[destination[1]] + str(destination[0] + 1)
        turn = "White" if self.role == 'w' else "Black"
        json = '{ "from":' + orig + ', "to":' + dest + ', "turn": "' + turn + '" }'
        print("MOVE SENT:", json)
        self._send_string(json)

    def _decode_json_board(self, board: list):
        k = np.zeros((9, 9), dtype=bool)
        w = np.zeros((9, 9), dtype=bool)
        b = np.zeros((9, 9), dtype=bool)
        board = np.array(board)
        k[board == 'KING'] = True
        w[board == 'WHITE'] = True
        b[board == 'BLACK'] = True
        return k, w, b
