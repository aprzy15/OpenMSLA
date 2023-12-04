import os
import zipfile
from config.config_print import PrintConfig
from controller_gcode import GcodeController
from config.config_machine import MachineConfig
import io
from pubsub import pub
from PIL import Image
import numpy as np
from controller_display import Display
from controller_ui import UiController
import logging

class Printer:
    def __init__(self, cfg_path):
        self.archive = None
        self.cfg = MachineConfig(cfg_path)
        self.controller = GcodeController(self.cfg)
        self.ui = UiController(self.cfg)
        self.display = Display(self.cfg)
        self.init_pubsub()

    def init_pubsub(self):
        pub.subscribe(self.z_home, 'z_home')
        pub.subscribe(self.z_move, 'z_pos_changed')
        pub.subscribe(self.start_print, 'start_print')
        pub.subscribe(self.start_macro, 'start_macro')

    def z_home(self):
        self.controller.send(f"G28 Z\r\n")
        res = self.controller.wait_for_home()
        if res:
            pub.sendMessage('homing_status', status=True)
        else:
            pub.sendMessage('homing_status', status=False)

    def z_move(self, arg1):
        self.controller.send(f"G0 Z{arg1} F1000\n")

    def start_print(self, fpath):
        self.ui.nav_printing()
        print_file = PrintFile(fpath)
        if not print_file.exists:
            print('File does not exist')
            self.ui.nav_home()
            return
        self.ui.max_layer = print_file.cfg.num_layers
        self.ui.fname = print_file.cfg.file_name
        # Read Gcode file
        gcode_commands = print_file.gcode_commands
        # Loop through gcode commands
        for gcode_str in gcode_commands:
            host_cmd = self.controller.execute(gcode_str)
            if host_cmd:
                self.parse_host_command(host_cmd, print_file)
        self.ui.nav_home()

    def start_macro(self, fpath):
        f = open(fpath)
        gcode = f.readlines()
        for raw_command in gcode:
            self.controller.execute(raw_command)

    def parse_host_command(self, cmd_str, print_file):
        if cmd_str.startswith('R1 '):
            self.R1(cmd_str, print_file)

    def R1(self, command, print_file):
        # Show image
        parts = command.rstrip('\r').strip(' ').split(' ')
        index = int(parts[1].lstrip('I'))
        self.ui.current_layer = index
        img = print_file.get_image(index)
        res = self.display.show(img)
        print(f'     {res}')

    # TODO auto start up for program (cron job)
    # TODO setup logging


class PrintArchive:
    def __init__(self, path):
        try:
            self.archive = zipfile.ZipFile(path, 'r')
            self.exists = True
        except Exception as err:
            self.exists = False

    def init_config(self):
        config_str = self.archive.read('printconfig.ini').decode('ascii')
        return PrintConfig(config_str)

    def init_gcode(self):
        f = io.TextIOWrapper(self.archive.open('printplan.gcode'), encoding="utf-8")
        return f.readlines()

    def get_image(self, index):
        im_path = self.archive.open(f'layer{str(index).zfill(6)}.png')
        img = np.array(Image.open(im_path))
        return img.astype('uint8')


class PrintFolder:
    def __init__(self, path):
        self.path = path
        self.exists = True

    def init_config(self):
        config_str = open(os.path.join(self.path, 'printconfig.ini')).read()
        return PrintConfig(config_str)

    def init_gcode(self):
        f = open(os.path.join(self.path, 'printplan.gcode'))
        return f.readlines()

    def get_image(self, index):
        im_path = os.path.join(self.path, f'layer{str(index).zfill(6)}.png')
        img = np.array(Image.open(im_path))
        return img.astype('uint8')


class PrintFile:
    def __init__(self, path):
        self.gcode_commands = []
        self.cfg = None
        self.printfile = None
        if os.path.isfile(path):
            self.printfile = PrintArchive(path)
        elif os.path.isdir(path):
            self.printfile = PrintFolder(path)
        else:
            print(f'Error: PrintFile path: {path} not supported')
        self.init_config()
        self.init_gcode()

    @property
    def exists(self):
        return self.printfile.exists

    def init_config(self):
        self.cfg = self.printfile.init_config()

    def init_gcode(self):
        self.gcode_commands = self.printfile.init_gcode()

    def get_image(self, index):
        return self.printfile.get_image(index)


if __name__ == '__main__':
    cfg_path = r'./machine_config.json'
    printer = Printer(cfg_path)

    # printer.start_macro()
    # pub.sendMessage('start_print', fpath='ex_build_folder')
    # pub.sendMessage('start_print', fpath=r'ex_build_folder/test_build.msla')

    # printer.start_print('ex_build_folder')
    # printer.start_print(r'ex_build_folder/test_build.msla')
