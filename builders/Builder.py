class Builder():
    def __init__(self, args, logger, config):
        self.args = args
        self.logger = logger
        self.config = config

        if "uri" not in self.config["repository"]:
            self.config["repository"]["uri"] = self.default_repository_uri

    def build(self):
        if not self._clone():
            return False

        if not self._copy_files():
            return False

        return True
