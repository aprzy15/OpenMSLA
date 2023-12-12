

class DisplayCommand:
    def __init__(self, command):
        self.command = command.split(' ')
        self.code = int(self.command[0].lstrip('D'))

    def execute(self):
        print(self.code)
        i=0


