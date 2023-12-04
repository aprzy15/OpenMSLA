import os
import json
import os


class MachineConfig:
    def __init__(self, path):
        self.base = json.load(open(path))

    @property
    def version(self):
        return self.base.get('version')

    @property
    def build_folder(self):
        return self.base.get('file_location')

    @property
    def encoder(self):
        return self.base.get('encoder')

    @property
    def clk(self):
        return self.encoder.get('clk_pin')

    @property
    def dt(self):
        return self.encoder.get('dt_pin')

    @property
    def sw(self):
        return self.encoder.get('sw_pin')

    @property
    def lcd_hmi(self):
        return self.base.get('lcd_hmi')

    @property
    def lcd_cols(self):
        return self.lcd_hmi.get('cols')

    @property
    def lcd_rows(self):
        return self.lcd_hmi.get('rows')

    @property
    def max_z(self):
        return self.base.get('max_z')

    @property
    def controller_port(self):
        return self.base.get('controller_port')

    @property
    def steps_mm(self):
        return self.base.get('z_steps_per_mm')

    @property
    def file_ext(self):
        return self.base.get('file_extension')

    @property
    def log_level(self):
        return self.base.get('logging_level')
