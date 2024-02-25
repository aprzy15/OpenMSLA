import time
from RPLCD.i2c import CharLCD
import threading
from RPi import GPIO
from config.config_machine import MachineConfig
import logging
import subprocess
import os
from pubsub import pub
import json
from ui_screens import *
from pubsub.utils import printTreeDocs

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
        self.cfg = cfg
        self.lcd = None
        self.z_pos = None
        self.is_homed = False
        self.files = []
        self.macros = []
        self.fname = ''
        self.print_layers = 1
        self.current_layer = 0
        self.encoder = Encoder(self.cfg)
        self.lcd = UiLCD(self.cfg)
        self.state = MainPage(self)
        pub.subscribe(self.ps_on_homed, 'homing_status')
        pub.subscribe(self.ps_on_print_start, 'ui.print_info')
        pub.subscribe(self.ps_on_layer_start, 'ui.layer_start')
        pub.subscribe(self.ps_print_end, 'ui.print_end')
        self.main_thread()

    def ps_print_end(self):
        self.current_layer = 0
        self.nav_home()

    def nav_home(self):
        self.navigate(MainPage)

    def nav_printing(self):
        self.navigate(PrintingPage)

    def navigate(self, class_obj, **kwargs):
        self.state = class_obj(self, **kwargs)
        self.state.update_screen()

    def ps_on_homed(self, status):
        if status:
            self.navigate(HomedPage)
        else:
            self.navigate(HomeFailedPage)

    def ps_on_print_start(self, print_layers, fname):
        self.print_layers = print_layers
        self.fname = fname
        self.navigate(PrintingPage, print_layers=self.print_layers, fname=self.fname, current_layer=self.current_layer)

    def ps_on_layer_start(self, current_layer):
        self.current_layer = current_layer
        self.navigate(PrintingPage, print_layers=self.print_layers, fname=self.fname, current_layer=self.current_layer)

    def main_thread(self):
        self.state.update_screen()
        while True:
            self.encoder.read_rotation(self.state)
            self.encoder.read_switch(self.state)

    def load_files(self):
        self.files = []
        if not os.path.exists(self.cfg.build_folder):
            return
        raw_files = os.listdir(self.cfg.build_folder)
        for file in raw_files:
            if os.path.splitext(file)[1] == self.cfg.file_ext:
                self.files.append(file)
            elif os.path.splitext(file)[1] == '.gcode':
                self.macros.append(file)
