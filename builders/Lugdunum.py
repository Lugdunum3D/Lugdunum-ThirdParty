import glob
import os
import subprocess
import platform
import shutil

from git import Repo

from .Builder import Builder

# Possible configuration
#   repository.uri (optional) => The uri of the git repository to clone
#   repository.tag (mandatory) => The tag to checkout to before building

class Lugdunum(Builder):
    default_repository_uri = 'https://github.com/Lugdunum3D/Lugdunum.git'

    def _clone(self):
        self.logger.info('Lugdunum: Clone main repository')

        repo = None
        if not os.path.isdir('lugdunum'):
            repo = Repo.clone_from(self.config['repository']['uri'], 'lugdunum')
        else:
            repo = Repo('lugdunum')

        repo.remotes['origin'].fetch()
        repo.git.checkout(self.config['repository']['tag'])

        return True

    def _compile(self, build_type):
        self.logger.info('Lugdunum: Configure for %s',  build_type)

        build_dir = os.path.join('lugdunum/build', build_type)

        if not os.path.isdir(build_dir):
            os.makedirs(build_dir)

        cmake_args = [
            'cmake',
            '-DCMAKE_BUILD_TYPE=' + build_type,
            '-DLUG_ACCEPT_DL=ON',
            '-DCMAKE_POSITION_INDEPENDENT_CODE=ON',
            '-DCMAKE_INSTALL_PREFIX=../../install',
            '../..'
        ]

        if platform.system() == 'Windows':
            cmake_args += ['-G', 'Visual Studio 15 2017 Win64']
        if platform.system() == 'Linux':
            cmake_args += ['-G', 'Ninja']

        if subprocess.Popen(cmake_args, cwd=build_dir).wait():
             return False

        self.logger.info('Lugdunum: Build for %s', build_type)
        if subprocess.Popen(['cmake', '--build', '.', '--config', build_type, '--target', 'install'], cwd=build_dir).wait():
             return False

        return True

    def _copy_files(self):
        lugdunum_root_path = os.path.join(self.args.path, 'lugdunum')

        self.logger.info('Lugdunum: Create directories')

        self.logger.info('Lugdunum: Copy files')

        if os.path.isdir(lugdunum_root_path):
            os.removedirs(lugdunum_root_path)
        shutil.copytree('lugdunum/install', lugdunum_root_path)

        return True
