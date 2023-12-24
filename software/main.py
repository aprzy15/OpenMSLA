from printer import Printer
from controller_ui import UiController
import os
from multiprocessing import Process
from pubsub import pub


def headless(cfg_path):
    printer = Printer(cfg_path)
    fpath = os.path.join('test_files', 'test-print')
    printer.start_print(fpath)


def with_ui(cfg_path):
    UiController(cfg_path)
    Printer(cfg_path)
    while True:
        pass


if __name__ == '__main__':
    cfg_path = r'/home/admin/printer/software/config/machine_config.json'
    # headless(cfg_path)
    # with_ui(cfg_path)
    # TODO UI print file not working
    # p = Process(target=Printer, args=[cfg_path])
    # p.start()
    printer = Printer(cfg_path)

    UiController(cfg_path)
    # p2 = Process(target=UiController, args=[cfg_path])
    # p2.start()

