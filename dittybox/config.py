import ConfigParser


class Section(object):
    def __init__(self, config_parser, section):
        self.config_parser = config_parser
        self.section = section

    def __getattr__(self, name):
        if self.config_parser.has_option(self.section, name):
            return self.config_parser.get(self.section, name)
        raise AttributeError()


class Configuration(object):
    def __init__(self, fp):
        self.fp = fp
        self.config_parser = ConfigParser.SafeConfigParser()
        self.config_parser.readfp(fp)

    def __getattr__(self, section):
        return Section(self.config_parser, section)
