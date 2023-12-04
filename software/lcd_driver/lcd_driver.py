#!/usr/bin/python3
import sys
myPath = '/home/admin/.local/lib/python3.11/site-packages'
sys.path.append(myPath)
import pygame as pg
import numpy as np
import os
import threading
import queue
import zmq
import json


class LCD:
    def __init__(self):
        self._socket = None
        self.screen = None
        self.width = 0
        self.height = 0
        self.init_connection()
        os.environ["DISPLAY"] = ":0"
        self.q = queue.Queue()
        threading.Thread(target=self.display_thread, daemon=True).start()
        self.hide()

    @property
    def socket(self):
        return self._socket

    @socket.setter
    def socket(self, value):
        self._socket = value

    @property
    def info(self):
        d = {
            'height': self.height,
            'width': int(self.width * 3),
        }
        return d

    def init_connection(self):
        context = zmq.Context()
        self.socket = context.socket(zmq.REP)
        self.socket.bind("tcp://*:5555")

    def handle_message(self, message):
        name = message[0]
        if name == b'frame':
            self.handle_frame(message[1])
        elif name == b'get_info':
            self.handle_get_info()
        else:
            self.socket.send_multipart([b'500', b'Command not supported'])

    def handle_frame(self, payload):
        try:
            arr = np.frombuffer(payload, dtype=np.uint8)
            display.show(arr)
            display.wait_for_command()
            self.socket.send_multipart([b'200', b'Success'])  # Send reply back to client
        except Exception as err:
            self.socket.send_multipart([b'500', bytes(str(err), 'utf-8')])

    def handle_get_info(self):
        user_encode_data = json.dumps(self.info, indent=2).encode('utf-8')
        self.socket.send_multipart([b'200', user_encode_data])

    def show(self, im):
        if len(im.shape) < 2:
            im = im.reshape((self.height, self.width * 3))
        r = im[:, 0::3]
        g = im[:, 1::3]
        b = im[:, 2::3]
        arr = np.rot90(np.dstack([r, g, b]))
        self.q.put(arr)

    def hide(self):
        arr = np.zeros((self.width, self.height, 3))
        self.q.put(arr)

    def wait_for_command(self):
        self.q.join()

    def display_thread(self):
        pg.display.init()
        screen = pg.display.set_mode()
        pg.display.toggle_fullscreen()
        pg.mouse.set_visible(False)
        self.width = screen.get_width()
        self.height = screen.get_height()
        while True:
            if self.q.empty():
                continue
            arr = self.q.get()
            surf = pg.Surface((arr.shape[0], arr.shape[1]))
            pg.surfarray.blit_array(surf, arr)
            pg.display.flip()
            screen.blit(surf, (0, 0))
            self.q.task_done()



if __name__ == '__main__':
    display = LCD()
    while True:
        message = display.socket.recv_multipart()
        display.handle_message(message)
