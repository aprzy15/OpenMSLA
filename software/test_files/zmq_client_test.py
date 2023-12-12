# client.py
import zmq
import imageio.v3 as iio
import numpy as np
import time
import json


class Display:
    def __init__(self):
        context = zmq.Context()
        self.socket = context.socket(zmq.REQ)
        self.socket.connect('tcp://localhost:5555')
        self.socket.send_multipart([b'get_info'])
        message = self.receive()
        d = json.loads(message)
        self.screen_shape = (d['width'], d['height'])

    def receive(self):
        raw_response = self.socket.recv_multipart()
        code = int(raw_response[0])
        if code != 200:
            raise ConnectionError(f'Code: {code} {raw_response[1]}')
        return raw_response[1]

    def show(self, im):
        im = im.astype(np.uint8)
        self.socket.send_multipart([b'frame', im.tobytes()])
        response = self.receive()
        print(f'Response: {response}')

    def hide(self):
        arr = np.zeros(self.screen_shape)
        im = arr.astype(np.uint8)
        self.socket.send_multipart([b'frame', im.tobytes()])
        response = self.receive()
        print(f'Response: {response}')

    def close_connection(self):
        self.socket.close()
        self.socket.term()

if __name__ == '__main__':
    im = iio.imread('LCD_test_im.png')
    im = im[:, :, 0]
    d = Display()
    t = 1
    d.show(im)
    time.sleep(t)
    d.hide()
    time.sleep(t)
    d.show(im)
    time.sleep(t)
    d.hide()
    time.sleep(t)
    d.show(im)


