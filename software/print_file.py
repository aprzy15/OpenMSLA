import os
import zipfile
from config.config_print import PrintConfig
import io
from PIL import Image
import numpy as np


class PrintData:
    def __init__(self, path):
        self.gcode_commands = []
        self.cfg = None
        self.print_data = None
        if os.path.isfile(path):
            self.print_data = PrintArchive(path)
        elif os.path.isdir(path):
            self.print_data = PrintFolder(path)
        else:
            print(f'Error: PrintFile path: {path} not supported')
        self.init_config()
        self.init_gcode()

    @property
    def exists(self):
        return self.print_data.exists

    def init_config(self):
        self.cfg = self.print_data.init_config()

    def init_gcode(self):
        self.gcode_commands = self.print_data.init_gcode()

    def get_image(self, index):
        return self.print_data.get_image(index)


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



