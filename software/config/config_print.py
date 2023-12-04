import configparser

class PrintConfig:
    def __init__(self, config_str):
        self.dir_path = None
        self.base = None
        self.load_from_str(config_str)

    def load_from_str(self, cfg_str):
        config = configparser.ConfigParser()
        config.read_string("[top]\n" + cfg_str)
        self.base = dict(config['top'])

    @property
    def num_layers(self):
        return int(self.base.get('num_layers'))

    @property
    def file_name(self):
        return self.base.get('file_name')

    @property
    def fileCreationTimestamp(self):
        return self.base.get('filecreationtimestamp')

    @property
    def layer_height(self):
        return self.base.get('layerheight')

    @property
    def material(self):
        return self.base.get('materialname')

    @property
    def printTime(self):
        return self.base.get('printtime')

    @property
    def printerModel(self):
        return self.base.get('printermodel')

    @property
    def slicer_version(self):
        return self.base.get('slicer_version')

    @property
    def usedMaterial(self):
        return self.base.get('usedmaterial')
