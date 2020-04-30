import os
import configparser


class Config(object):

    CONFIG_FILE = 'local.config'
    PYGRASP_PATH = os.path.split(os.path.abspath(__file__))[0]

    def __init__(self):
        self.p = configparser.SafeConfigParser()
        if not self.p.read(os.path.join(self.pygrasp._PATH, self.CONFIG_FILE)):
            raise ValueError("Could not parse config file.")

    def get(self, section, option):
        return self.p.get(section, option)
