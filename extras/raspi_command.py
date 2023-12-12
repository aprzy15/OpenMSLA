import time
class RaspPiCommand:
    def __init__(self, command):
        self.command = command.split(' ')
        self.code = int(command.split(' ')[0][1:])

    def execute(self):
        if self.code == 4:
            return self.wait()
        print(self.code)

    def wait(self):
        ms = int(self.command[1].lstrip('T'))
        time.sleep(ms/1000)