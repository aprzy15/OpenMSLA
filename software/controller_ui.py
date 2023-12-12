import time
from RPLCD.i2c import CharLCD
import threading
from RPi import GPIO
import logging
import subprocess
import os
from pubsub import pub
import json
from ui_screens import MainPage, PrintingPage


def find_drive(d, target):
    devices = d['blockdevices']
    for device in devices:
        children = device['children']
        for child in children:
            name = child['name']
            label = child['label']
            if label == target:
                return name
    return None


class Encoder:
    def __init__(self, cfg):
        self.sw_last_state = -1
        self.clk_last_state = 0
        self.last_sw_time = 0
        self.cfg = cfg
        self.init_encoder()

    def init_encoder(self):
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(self.cfg.clk, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
        GPIO.setup(self.cfg.dt, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
        GPIO.setup(self.cfg.sw, GPIO.IN, pull_up_down=GPIO.PUD_UP)
        self.clk_last_state = GPIO.input(self.cfg.clk)

    def read_switch(self, state):
        sw_state = GPIO.input(self.cfg.sw)
        t = time.time()
        elapsed_time = t - self.last_sw_time
        if sw_state == 1 and self.sw_last_state == 0 and elapsed_time > 0.1:
            state.enter()
            self.sw_last_state = 1
            self.last_sw_time = t
        else:
            self.sw_last_state = sw_state

    def read_rotation(self, state):
        clk_state = GPIO.input(self.cfg.clk)
        dt_state = GPIO.input(self.cfg.dt)
        if clk_state != self.clk_last_state:
            if dt_state != clk_state:
                state.up()
            else:
                state.dn()
        self.clk_last_state = clk_state


class UiLCD(CharLCD):
    def __init__(self, cfg):
        version = cfg.version
        lcd_cfg = cfg.lcd_hmi
        super().__init__(**lcd_cfg)
        self.clear()
        self.write_string(f'OpenMSLA v{version}')
        time.sleep(1)
        self.clear()


class UiController:
    def __init__(self, cfg):
        self.lcd = None
        self.z_pos = None
        self.files = []
        self.macros = []
        self.fname = ''
        self.max_layer = 1
        self._current_layer = 0
        self.cfg = cfg
        self.encoder = Encoder(self.cfg)
        self.lcd = UiLCD(self.cfg)
        self.state = MainPage(self)
        threading.Thread(target=self.main_thread).start()

    def nav_home(self):
        self.navigate(MainPage)

    def nav_printing(self):
        self.navigate(PrintingPage)

    def navigate(self, class_obj):
        self.state = class_obj(self)
        self.state.update_screen()

    @property
    def current_layer(self):
        return self._current_layer

    @current_layer.setter
    def current_layer(self, current_layer):
        self._current_layer = current_layer
        self.state.update_screen()

    def main_thread(self):
        self.state.update_screen()
        while True:
            self.encoder.read_rotation(self.state)
            self.encoder.read_switch(self.state)

    def load_files(self):
        self.files = []
        res = subprocess.check_output(f"lsblk -o name,label --json", shell=True).decode()
        d = json.loads(res)
        label = 'thumb'
        port = find_drive(d, label)
        if port is None:
            print(f'Error: Cannot locate drive label: {label}')
            return
        os.system(f"sudo mount -t exfat /dev/{port} /home/usbdrive")
        raw_files = os.listdir(self.cfg.build_folder)
        print(raw_files)
        for file in raw_files:
            if os.path.splitext(file)[1] == self.cfg.file_ext:
                self.files.append(file)
            elif os.path.splitext(file)[1] == '.gcode':
                self.macros.append(file)
