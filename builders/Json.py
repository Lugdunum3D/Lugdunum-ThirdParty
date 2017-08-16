import os
import shutil

from git import Repo

from .Builder import Builder

# Possible configuration
#   repository.uri (optional) => The uri of the git repository to clone
#   repository.tag (mandatory) => The tag to checkout to before building

class Json(Builder):
    default_repository_uri = 'https://github.com/nlohmann/json.git'

    def _clone(self):
        self.logger.info('json: Clone main repository')

        repo = None
        if not os.path.isdir('json'):
            repo = Repo.clone_from(self.config['repository']['uri'], 'json')
        else:
            repo = Repo('json')

        repo.remotes['origin'].fetch()
        repo.git.checkout(self.config['repository']['tag'])

        return True

    def _copy_files(self):
        json_root_path = os.path.join(self.args.path, 'json')
        json_include_path = os.path.join(json_root_path, 'include')

        self.logger.info('json: Create directories')

        if not os.path.isdir(json_include_path):
            os.makedirs(json_include_path)

        self.logger.info('json: Copy license file')

        shutil.copy('json/LICENSE.MIT', json_root_path)

        self.logger.info('json: Copy include files')

        real_include_path = os.path.join(json_include_path, 'json')

        if not os.path.isdir(real_include_path):
            shutil.copytree('json/src', real_include_path)

        return True
