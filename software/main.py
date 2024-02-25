from printer import Printer
from controller_ui import UiController
import os
from multiprocessing import Process
from pubsub import pub
from config.config_machine import MachineConfig


def headless(cfg):
    printer = Printer(cfg)
    # fpath = os.path.join('test_files', 'test-print')
    # fpath = r'/home/admin/printer/software/test_files/test-print'
    fpath = cfg.headless_filepath
    printer.start_print(fpath)


def with_ui(cfg):
    printer = Printer(cfg)
    UiController(cfg)


if __name__ == '__main__':
    cfg_path = r'/home/admin/printer/software/config/machine_config.json'
    cfg = MachineConfig(cfg_path)
    if cfg.run_headless:
        headless(cfg)
    else:
        with_ui(cfg)
    # printer = Printer(cfg)
    # UiController(cfg)

