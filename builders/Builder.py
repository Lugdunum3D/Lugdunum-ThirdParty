class Builder():
    def __init__(self, args, logger, config):
        self.args = args
        self.logger = logger
        self.config = config

        if 'uri' not in self.config['repository']:
            self.config['repository']['uri'] = self.default_repository_uri

    def _compile(self, build_type):
        return True

    def build(self):
        if not self._clone():
            return False

        for build_type in self.args.build_types:
            if not self._compile(build_type):
                return False

        if not self._copy_files():
            return False

        return True
