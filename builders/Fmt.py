import os
import shutil

from git import Repo

class Fmt():
    git_uri = "https://github.com/fmtlib/fmt.git"

    def __init__(self, args, logger):
        self.args = args
        self.logger = logger

    def _clone(self):
        self.logger.info("Fmt: Clone main repository")
        if not os.path.isdir("fmt"):
            Repo.clone_from(Fmt.git_uri, "fmt")

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
