from controller_gcode import GcodeController, GcodeCommand
from config.config_machine import MachineConfig
from pubsub import pub
from controller_display import Display
from print_file import PrintData
import time


class Printer:
    def __init__(self, cfg):
        # pub.subscribe(self.home_z, 'printer.home')
        self.cancel_flag = False
        self.archive = None
        self.cfg = cfg
        self.controller = GcodeController(self.cfg)
        self.display = Display(self.cfg)
        self.init_pubsub()
        print('Printer Initialized')

    def init_pubsub(self):
        pub.subscribe(self.controller.move_z, 'ui.z_changed')
        pub.subscribe(self.controller.home, 'printer.home')
        # pub.subscribe(self.home_z, 'printer.home')
        pub.subscribe(self.start_print, 'printer.start_print')
        pub.subscribe(self.cancel_print, 'printer.cancel_print')
        pub.subscribe(self.start_macro, 'printer.start_macro')

    def home_z(self):
        print('home z host')
        self.controller.home()

    def start_print(self, fpath):
        print_file = PrintData(fpath)
        if not print_file.exists:
            print('File does not exist')
            pub.sendMessage('ui.print_end')
            return
        pub.sendMessage('ui.print_info', print_layers=print_file.cfg.num_layers, fname=print_file.cfg.file_name)
        # Read Gcode file
        gcode_commands = print_file.gcode_commands
        # Loop through gcode commands
        self.cancel_flag = False
        for gcode_str in gcode_commands:
            if self.cancel_flag:
                break
            command = GcodeCommand(gcode_str)
            response = self.controller.execute(command)
            if command.is_host_command:
                self.parse_host_command(response, print_file)
        command = GcodeCommand("M106 P0 S0\r\n")
        response = self.controller.execute(command)
        pub.sendMessage('ui.print_end')

    def cancel_print(self):
        self.cancel_flag = True

    def start_macro(self, fpath):
        f = open(fpath)
        gcode = f.readlines()
        for raw_command in gcode:
            command = GcodeCommand(raw_command)
            self.controller.execute(command)

    def parse_host_command(self, cmd_str, print_file):
        if cmd_str.startswith('R1 '):
            self.R1(cmd_str, print_file)

    def R1(self, command, print_file):
        # Show image
        parts = command.rstrip('\r').strip(' ').split(' ')
        index = int(parts[1].lstrip('I'))
        pub.sendMessage('ui.layer_start', current_layer=index)
        img = print_file.get_image(index)
        res = self.display.show(img)
        time.sleep(0.2)  # Only needed if move command is really quick


if __name__ == '__main__':
    cfg_path = r'./config/machine_config.json'
    printer = Printer(cfg_path)

