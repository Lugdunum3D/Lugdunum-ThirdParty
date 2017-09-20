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

class Restclient(Builder):
    default_repository_uri = 'https://github.com/mrtazz/restclient-cpp.git'

    def _clone(self):
        self.logger.info('Restclient: Clone main repository')

        repo = None
        if not os.path.isdir('restclient'):
            repo = Repo.clone_from(self.config['repository']['uri'], 'restclient')
        else:
            repo = Repo('restclient')

        repo.remotes['origin'].fetch()
        repo.git.checkout(self.config['repository']['tag'])

        return True

    def _compile(self, build_type):
        self.logger.info('Restclient: Configure for %s',  build_type)

        shutil.copy(os.path.join(os.path.dirname(os.path.realpath(__file__)), "../assets/restclient/include/version.h"), 'restclient/include/restclient-cpp')
        shutil.copy(os.path.join(os.path.dirname(os.path.realpath(__file__)), "../assets/restclient/CMakeLists.txt"), 'restclient')

        build_dir = os.path.join('restclient/build', build_type)

        if not os.path.isdir(build_dir):
            os.makedirs(build_dir)

        cmake_args = [
            'cmake',
            '-DCMAKE_BUILD_TYPE=' + build_type,
            '-DCMAKE_PREFIX_PATH=' + os.path.join(os.path.dirname(os.path.realpath(__file__))) + "../../thirdparty/curl",
            '../..'
        ]

        if platform.system() == 'Windows':
            cmake_args += ['-G', 'Visual Studio 15 2017 Win64']

        if subprocess.Popen(cmake_args, cwd=build_dir).wait():
             return False

        self.logger.info('Restclient: Build for %s', build_type)
        if subprocess.Popen(['cmake', '--build', '.', '--config', build_type], cwd=build_dir).wait():
             return False

        return True

    def _copy_files(self):
        restclient_loader_root_path = os.path.join(self.args.path, 'restclient')
        restclient_loader_include_path = os.path.join(restclient_loader_root_path, 'include')
        restclient_loader_library_path = os.path.join(restclient_loader_root_path, 'lib')

        self.logger.info('Restclient: Create directories')

        if not os.path.isdir(restclient_loader_include_path):
            os.makedirs(restclient_loader_include_path)

        if not os.path.isdir(restclient_loader_library_path):
            os.makedirs(restclient_loader_library_path)

        self.logger.info('Restclient: Copy license file')

        shutil.copy('restclient/LICENSE', restclient_loader_root_path)

        self.logger.info('Restclient: Copy include files')

        real_include_path = os.path.join(restclient_loader_include_path, 'restclient-cpp')

        if not os.path.isdir(real_include_path):
            shutil.copytree('restclient/include/restclient-cpp', real_include_path)

        for build_type in self.args.build_types:
            self.logger.info('Restclient: Copy libraries for %s', build_type)

            suffix = '-d' if build_type == 'Debug' else ''

            if platform.system() == 'Linux':
                shutil.copy(os.path.join('restclient/build', build_type, 'librestclient-cpp' + '.a'),
                            os.path.join(restclient_loader_library_path, 'librestclient-cpp' + suffix + '.a'))
            elif platform.system() == 'Windows':
                shutil.copy(os.path.join('restclient/build', build_type, build_type, 'restclient-cpp' + '.lib'),
                            os.path.join(restclient_loader_library_path, 'restclient-cpp' + suffix + '.lib'))

                if build_type == 'Debug':
                    self.logger.info('Restclient: Copy pdb files')

                    for file in glob.glob(os.path.join('restclient/build', build_type, 'lib', build_type, '*.pdb')):
                        shutil.copy(file, restclient_loader_library_path)
            else:
                return False

        return True
