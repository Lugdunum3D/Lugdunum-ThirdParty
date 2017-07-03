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

class Shaderc(Builder):
    default_repository_uri = 'https://github.com/google/shaderc.git'

    def _clone(self):
        self.logger.info('Shaderc: Clone main repository')

        repo = None
        if not os.path.isdir('shaderc'):
            repo = Repo.clone_from(self.config['repository']['uri'], 'shaderc')
        else:
            repo = Repo('shaderc')

        repo.remotes['origin'].fetch(self.config['repository']['tag'])
        repo.git.checkout(self.config['repository']['tag'])

        # TODO: Use tag and repo in the yml

        self.logger.info('Shaderc: Clone googletest repository')
        if not os.path.isdir('shaderc/third_party/googletest'):
            repo_gtest = Repo.clone_from('https://github.com/google/googletest.git', 'shaderc/third_party/googletest')
            repo_gtest.git.checkout("c2d90bddc6a2a562ee7750c14351e9ca16a6a37a")

        self.logger.info('Shaderc: Clone glslang repository')
        if not os.path.isdir('shaderc/third_party/glslang'):
            repo_glslang = Repo.clone_from('https://github.com/google/glslang.git', 'shaderc/third_party/glslang')
            repo_glslang.git.checkout("91c46c656720a6e1e71a3411cd1f4f792b427b2d")

        self.logger.info('Shaderc: Clone spirv-tools repository')
        if not os.path.isdir('shaderc/third_party/spirv-tools'):
            repo_spirv_tools = Repo.clone_from('https://github.com/KhronosGroup/SPIRV-Tools.git', 'shaderc/third_party/spirv-tools')
            repo_spirv_tools.git.checkout("7c8da66bc27cc5c4ccb6a0fa612f56c9417518ff")

        self.logger.info('Shaderc: Clone spirv-headers repository')
        if not os.path.isdir('shaderc/third_party/spirv-tools/external/spirv-headers'):
            repo_spirv_headers = Repo.clone_from('https://github.com/KhronosGroup/SPIRV-Headers.git', 'shaderc/third_party/spirv-tools/external/spirv-headers')
            repo_spirv_headers.git.checkout("63e1062a194750b354d48be8c16750d7a4d0dc4e")

        return True

    def _compile(self, build_type):
        self.logger.info('Shaderc: Configure for %s',  build_type)

        build_dir = os.path.join('shaderc/build', build_type)

        if not os.path.isdir(build_dir):
            os.makedirs(build_dir)

        cmake_args = [
            'cmake',
            '-DSHADERC_ENABLE_SHARED_CRT=ON',
            '-DENABLE_GLSLANG_BINARIES=OFF',
            '-DSHADERC_SKIP_TESTS=ON',
            '-DCMAKE_BUILD_TYPE=' + build_type,
            '-DCMAKE_POSITION_INDEPENDENT_CODE=ON',
            '-DSHADERC_ENABLE_SHARED_CRT=ON',
            '../..'
        ]

        if platform.system() == 'Windows':
            cmake_args += ['-G', 'Visual Studio 15 2017 Win64']

        if subprocess.Popen(cmake_args, cwd=build_dir).wait():
             return False

        self.logger.info('Shaderc: Build for %s', build_type)
        if subprocess.Popen(['cmake', '--build', '.', '--config', build_type], cwd=build_dir).wait():
             return False

        return True

    def _copy_files(self):
        shaderc_root_path = os.path.join(self.args.path, 'shaderc')
        shaderc_include_path = os.path.join(shaderc_root_path, 'include')
        shaderc_library_path = os.path.join(shaderc_root_path, 'lib')

        self.logger.info('Shaderc: Create directories')

        if not os.path.isdir(shaderc_include_path):
            os.makedirs(shaderc_include_path)

        if not os.path.isdir(shaderc_library_path):
            os.makedirs(shaderc_library_path)

        self.logger.info('Shaderc: Copy license file')

        shutil.copy('shaderc/LICENSE', shaderc_root_path)

        self.logger.info('Shaderc: Copy include files')

        real_include_path = os.path.join(shaderc_include_path, 'shaderc')

        if not os.path.isdir(real_include_path):
            shutil.copytree('shaderc/libshaderc/include/shaderc', real_include_path)

        for build_type in self.args.build_types:
            self.logger.info('Shaderc: Copy libraries for %s', build_type)

            suffix = '-d' if build_type == 'Debug' else ''

            if platform.system() == 'Linux':
                shutil.copy(os.path.join('shaderc/build', build_type, 'libshaderc/libshaderc_combined.a'),                  os.path.join(shaderc_library_path, 'libshaderc_combined' + suffix + '.a'))
            elif platform.system() == 'Windows':
                shutil.copy(os.path.join('shaderc/build', build_type, 'libshaderc', build_type, 'shaderc_combined.lib'),    os.path.join(shaderc_library_path, 'shaderc_combined' + suffix + '.lib'))

                if build_type == 'Debug':
                    self.logger.info('Shaderc: Copy pdb files')

                    for file in glob.glob(os.path.join('shaderc/build', build_type, 'libshaderc', build_type, '*.pdb')):
                        shutil.copy(file, shaderc_library_path)
            else:
                return False

        return True
