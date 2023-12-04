import serial
import time
import logging


class GcodeCommand:
    def __init__(self, command):
        self.raw_string = command
        parts = command.rstrip('\n').split(' ')
        self.is_host_command = False
        self.response_code = 'ok'
        if command.startswith('M118 '):
            self.response_code = parts[1]
            self.is_host_command = True
        elif command.startswith('G28 '):
            self.response_code = 'X'


class GcodeController:
    def __init__(self, cfg):
        self.serial = None
        self.cfg = cfg
        self.commands = []
        self.init_controller()

    def init_controller(self):
        self.serial = serial.Serial(self.cfg.controller_port, 115200)
        time.sleep(1)
        self.serial.reset_input_buffer()
        time.sleep(0.6)
        self.send("M501\n")
        self.send(f"M92 Z{self.cfg.steps_mm}\n")
        self.send("M500\n")
        self.send("M211 S0\n")
        time.sleep(0.5)
        self._wait_for_gcode_response('ok', 20)

    def execute(self, gcode_str, timeout=60):
        command = GcodeCommand(gcode_str)
        self.send(command.raw_string)
        response = self._wait_for_gcode_response(command.response_code, timeout)
        if command.is_host_command:
            return response
        else:
            return ''

    def send(self, gcode_string):
        self.serial.write(str.encode(gcode_string))

    def read(self):
        return self.serial.read_until().decode('ascii').rstrip('\n')

    def wait_for_home(self):
        return self._wait_for_gcode_response('X', timeout=60)

    def _wait_for_gcode_response(self, response, timeout):
        res = self.read()
        t0 = time.time()
        while not res.startswith(response):
            time.sleep(0.25)
            res = self.read().strip(' ')
            if time.time() - t0 > timeout:
                print('COMMAND TIMEOUT ERROR')
                # TODO cancel print if timeout error occurs
        return res