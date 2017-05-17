import os
import shutil

from git import Repo

class Fmt():
    git_uri = "https://github.com/fmtlib/fmt.git"

    def __init__(self, args, logger, config):
        self.args = args
        self.logger = logger
        self.config = config

        if "uri" not in self.config["repository"]:
            self.config["repository"]["uri"] = Fmt.git_uri

    def _clone(self):
        self.logger.info("Fmt: Clone main repository")

        repo = None
        if not os.path.isdir("fmt"):
            repo = Repo.clone_from(self.config["repository"]["uri"], "fmt")
        else:
            repo = Repo("fmt")

        repo.git.checkout(self.config["repository"]["tag"])

        return True

    def _copy_files(self):
        fmt_root_path = os.path.join(self.args.path, "fmt")
        fmt_include_path = os.path.join(fmt_root_path, "include")

        self.logger.info("Fmt: Create directories")

        if not os.path.isdir(fmt_include_path):
            os.makedirs(fmt_include_path)

        self.logger.info("Fmt: Copy license file")

        shutil.copy("fmt/LICENSE.rst", fmt_root_path)

        self.logger.info("Fmt: Copy include files")

        real_include_path = os.path.join(fmt_include_path, "fmt")

        if not os.path.isdir(real_include_path):
            shutil.copytree("fmt/fmt", real_include_path)
            os.remove(os.path.join(real_include_path, "CMakeLists.txt"))

        return True

    def build(self):
        if not self._clone():
            return False

        if not self._copy_files():
            return False

        return True
