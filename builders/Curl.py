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

class Curl(Builder):
    default_repository_uri = 'https://github.com/Lugdunum3D/curl.git'

    def _clone(self):
        self.logger.info('Curl: Clone main repository')

        repo = None
        if not os.path.isdir('curl'):
            repo = Repo.clone_from(self.config['repository']['uri'], 'curl')
        else:
            repo = Repo('curl')

        repo.remotes['origin'].fetch()
        repo.git.checkout(self.config['repository']['tag'])

        return True

    def _compile(self, build_type):
        self.logger.info('Curl: Configure for %s',  build_type)

        build_dir = os.path.join('curl/build', build_type)

        if not os.path.isdir(build_dir):
            os.makedirs(build_dir)

        cmake_args = [
            'cmake',
            '-DCMAKE_BUILD_TYPE=' + build_type,
            '-DCMAKE_POSITION_INDEPENDENT_CODE=ON',
            '../..'
        ]

        if platform.system() == 'Windows':
            cmake_args += ['-G', 'Visual Studio 15 2017 Win64']
        if platform.system() == 'Linux':
            cmake_args += ['-G', 'Ninja']

        if subprocess.Popen(cmake_args, cwd=build_dir).wait():
             return False

        self.logger.info('Curl: Build for %s', build_type)
        if platform.system() == 'Windows':
            if subprocess.Popen(['cmake', '--build', '.', '--target', 'curl', '--config', build_type], cwd=build_dir).wait():
                 return False
        else:
            if subprocess.Popen(['cmake', '--build', '.', '--config', build_type], cwd=build_dir).wait():
                 return False

        return True

    def _copy_files(self):
        curl_loader_root_path = os.path.join(self.args.path, 'curl')
        curl_loader_include_path = os.path.join(curl_loader_root_path, 'include')
        curl_loader_library_path = os.path.join(curl_loader_root_path, 'lib')

        self.logger.info('Curl: Create directories')

        if not os.path.isdir(curl_loader_include_path):
            os.makedirs(curl_loader_include_path)

        if not os.path.isdir(curl_loader_library_path):
            os.makedirs(curl_loader_library_path)

        self.logger.info('Curl: Copy license file')

        shutil.copy('curl/docs/LICENSE-MIXING.md', curl_loader_root_path)

        self.logger.info('Curl: Copy include files')

        real_include_path = os.path.join(curl_loader_include_path, 'curl')

        if not os.path.isdir(real_include_path):
            shutil.copytree('curl/include/curl', real_include_path)

        for build_type in self.args.build_types:
            self.logger.info('Curl: Copy libraries for %s', build_type)

            if platform.system() == 'Linux':
                suffix = '-d' if build_type == 'Debug' else ''
                shutil.copy(os.path.join('curl', 'build', build_type, 'lib', 'libcurl' + suffix + '.so'),
                            curl_loader_library_path)
            elif platform.system() == 'Windows':
                for file in glob.glob(os.path.join('curl', 'build', build_type, 'lib', build_type, '*')):
                    shutil.copy(file, curl_loader_library_path)

        return True
