import time
from state_machine import StateMachine
from state_machine import MainPage, PrintingPage
from RPLCD.i2c import CharLCD
import threading
from RPi import GPIO
import logging


class UiController:
    def __init__(self, cfg):
        self.sw_last_state = -1
        self.clk_last_state = 0
        self.last_sw_time = 0
        self.lcd = None
        self.cfg = cfg
        self.init_encoder()
        self.init_lcd_hmi()
        self.sm = StateMachine(self.cfg, self.lcd)
        # self.main_thread()
        threading.Thread(target=self.main_thread).start()

    def nav_home(self):
        self.sm.navigate(MainPage)

    def nav_printing(self):
        self.sm.navigate(PrintingPage)

    @property
    def max_layer(self):
        return self.sm.max_layer

    @max_layer.setter
    def max_layer(self, max_layer):
        self.sm.max_layer = max_layer

    @property
    def fname(self):
        return self.sm.fname

    @fname.setter
    def fname(self, fname):
        self.sm.fname = fname

    @property
    def current_layer(self):
        return self.sm.current_layer

    @current_layer.setter
    def current_layer(self, current_layer):
        self.sm.current_layer = current_layer
        self.sm.state.update_screen()

    def init_encoder(self):
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(self.cfg.clk, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
        GPIO.setup(self.cfg.dt, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
        GPIO.setup(self.cfg.sw, GPIO.IN, pull_up_down=GPIO.PUD_UP)
        self.clk_last_state = GPIO.input(self.cfg.clk)

    def init_lcd_hmi(self):
        version = self.cfg.version
        lcd_cfg = self.cfg.lcd_hmi
        self.lcd = CharLCD(**lcd_cfg)
        self.lcd.clear()
        self.lcd.write_string(f'OpenMSLA v{version}')
        time.sleep(1)
        self.lcd.clear()

    def main_thread(self):
        self.sm.state.update_screen()
        while True:
            self.read_encoder()
            self.read_switch()

    def read_switch(self):
        sw_state = GPIO.input(self.cfg.sw)
        t = time.time()
        elapsed_time = t - self.last_sw_time
        if sw_state == 1 and self.sw_last_state == 0 and elapsed_time > 0.1:
            self.sm.state.enter()
            self.sw_last_state = 1
            self.last_sw_time = t
        else:
            self.sw_last_state = sw_state

    def read_encoder(self):
        clk_state = GPIO.input(self.cfg.clk)
        dt_state = GPIO.input(self.cfg.dt)
        if clk_state != self.clk_last_state:
            if dt_state != clk_state:
                self.sm.state.up()
            else:
                self.sm.state.dn()
        self.clk_last_state = clk_state
