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

class Gltf2Loader(Builder):
    default_repository_uri = 'https://github.com/Lugdunum3D/glTF2-loader.git'

    def _clone(self):
        self.logger.info('Gltf2Loader: Clone main repository')

        repo = None
        if not os.path.isdir('glTF2-loader'):
            repo = Repo.clone_from(self.config['repository']['uri'], 'glTF2-loader')
        else:
            repo = Repo('glTF2-loader')

        repo.remotes['origin'].fetch()
        repo.git.checkout(self.config['repository']['tag'])

        return True

    def _compile(self, build_type):
        self.logger.info('Gltf2Loader: Configure for %s',  build_type)

        build_dir = os.path.join('glTF2-loader/build', build_type)

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

        if self.android_config['enabled']:
            cmake_args[0] = self.android_config['cmake_executable']
            cmake_args += ['-G', 'Android Gradle - Unix Makefiles']
            cmake_args += ['-DCMAKE_TOOLCHAIN_FILE=%s' % self.android_config['cmake_toolchain']]
            cmake_args += ['-DANDROID_PLATFORM=android-24']
            cmake_args += ['-DANDROID_ABI=arm64-v8a']
            cmake_args += ['-DANDROID_STL=c++_shared']

        if subprocess.Popen(cmake_args, cwd=build_dir).wait():
             return False

        self.logger.info('Gltf2Loader: Build for %s', build_type)
        if subprocess.Popen(['cmake', '--build', '.', '--config', build_type], cwd=build_dir).wait():
             return False

        return True

    def _copy_files(self):
        gltf2_loader_root_path = os.path.join(self.args.path, 'glTF2-loader')
        gltf2_loader_include_path = os.path.join(gltf2_loader_root_path, 'include')
        gltf2_loader_library_path = os.path.join(gltf2_loader_root_path, 'lib')

        self.logger.info('Gltf2Loader: Create directories')

        if not os.path.isdir(gltf2_loader_include_path):
            os.makedirs(gltf2_loader_include_path)

        if not os.path.isdir(gltf2_loader_library_path):
            os.makedirs(gltf2_loader_library_path)

        self.logger.info('Gltf2Loader: Copy license file')

        shutil.copy('glTF2-loader/LICENSE', gltf2_loader_root_path)

        self.logger.info('Gltf2Loader: Copy include files')

        real_include_path = os.path.join(gltf2_loader_include_path, 'gltf2')

        if not os.path.isdir(real_include_path):
            shutil.copytree('glTF2-loader/include/gltf2', real_include_path)

        for build_type in self.args.build_types:
            self.logger.info('Gltf2Loader: Copy libraries for %s', build_type)

            suffix = '-d' if build_type == 'Debug' else ''

            if self.android_config['enabled'] or platform.system() == 'Linux':
                shutil.copy(os.path.join('glTF2-loader/build', build_type, 'libgltf2-loader' + suffix + '.a'),              os.path.join(gltf2_loader_library_path, 'libgltf2-loader' + suffix + '.a'))
            elif platform.system() == 'Windows':
                shutil.copy(os.path.join('glTF2-loader/build', build_type, build_type, 'gltf2-loader' + suffix + '.lib'),   os.path.join(gltf2_loader_library_path, 'gltf2-loader' + suffix + '.lib'))

                if build_type == 'Debug':
                    self.logger.info('Gltf2Loader: Copy pdb files')

                    for file in glob.glob(os.path.join('glTF2-loader/build', build_type, build_type, '*.pdb')):
                        shutil.copy(file, gltf2_loader_library_path)
            else:
                return False

        return True
