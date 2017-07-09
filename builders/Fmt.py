import os
import shutil

from git import Repo

from .Builder import Builder

# Possible configuration
#   repository.uri (optional) => The uri of the git repository to clone
#   repository.tag (mandatory) => The tag to checkout to before building

class Fmt(Builder):
    default_repository_uri = 'https://github.com/fmtlib/fmt.git'

    def _clone(self):
        self.logger.info('Fmt: Clone main repository')

        repo = None
        if not os.path.isdir('fmt'):
            repo = Repo.clone_from(self.config['repository']['uri'], 'fmt')
        else:
            repo = Repo('fmt')

        repo.remotes['origin'].fetch()
        repo.git.checkout(self.config['repository']['tag'])

        return True

    def _copy_files(self):
        fmt_root_path = os.path.join(self.args.path, 'fmt')
        fmt_include_path = os.path.join(fmt_root_path, 'include')

        self.logger.info('Fmt: Create directories')

        if not os.path.isdir(fmt_include_path):
            os.makedirs(fmt_include_path)

        self.logger.info('Fmt: Copy license file')

        shutil.copy('fmt/LICENSE.rst', fmt_root_path)

        self.logger.info('Fmt: Copy include files')

        real_include_path = os.path.join(fmt_include_path, 'fmt')

        if not os.path.isdir(real_include_path):
            shutil.copytree('fmt/fmt', real_include_path)
            os.remove(os.path.join(real_include_path, 'CMakeLists.txt'))

        return True
