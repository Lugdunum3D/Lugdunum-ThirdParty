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

class Freetype(Builder):
    default_repository_uri = 'http://git.sv.nongnu.org/r/freetype/freetype2.git'

    def _clone(self):
        self.logger.info('Freetype: Clone main repository')

        repo = None
        if not os.path.isdir('freetype'):
            repo = Repo.clone_from(self.config['repository']['uri'], 'freetype')
        else:
            repo = Repo('freetype')

        repo.remotes['origin'].fetch()
        repo.git.checkout(self.config['repository']['tag'])

        return True

    def _compile(self, build_type):
        self.logger.info('Freetype: Configure for %s',  build_type)

        build_dir = os.path.join('freetype/build', build_type)

        if not os.path.isdir(build_dir):
            os.makedirs(build_dir)

        cmake_args = [
            'cmake',
            '-DCMAKE_BUILD_TYPE=' + build_type,
            '-DWITH_ZLIB=OFF',
            '-DWITH_HarfBuzz=OFF',
            '-DWITH_BZip2=OFF',
            '-DWITH_PNG=OFF',
            '../..'
        ]

        if platform.system() == 'Windows':
            cmake_args += ['-G', 'Visual Studio 15 2017 Win64']
        if platform.system() == 'Linux':
            cmake_args += ['-G', 'Ninja']

        if self.build_android:
            cmake_args[0] = os.environ.get("ANDROID_SDK_ROOT") + '/cmake/3.6.4111459/bin/cmake'
            cmake_args += ['-G', 'Android Gradle - Unix Makefiles']
            cmake_args += ['-DCMAKE_TOOLCHAIN_FILE=%s' % os.environ.get("ANDROID_SDK_ROOT") + '/ndk-bundle/build/cmake/android.toolchain.cmake']
            cmake_args += ['-DANDROID_PLATFORM=android-24']
            cmake_args += ['-DANDROID_ABI=arm64-v8a']
            cmake_args += ['-DANDROID_STL=c++_shared']

        if subprocess.Popen(cmake_args, cwd=build_dir).wait():
             return False

        self.logger.info('Freetype: Build for %s', build_type)
        if subprocess.Popen(['cmake', '--build', '.', '--config', build_type], cwd=build_dir).wait():
             return False

        return True

    def _copy_files(self):
        freetype_root_path = os.path.join(self.args.path, 'freetype')
        freetype_include_path = os.path.join(freetype_root_path, 'include')
        freetype_library_path = os.path.join(freetype_root_path, 'lib')

        self.logger.info('Freetype: Create directories')

        if os.path.exists(freetype_include_path):
                shutil.rmtree(freetype_include_path)

        if not os.path.isdir(freetype_library_path):
            os.makedirs(freetype_library_path)

        self.logger.info('Freetype: Copy license file')

        shutil.copy('freetype/docs/FTL.TXT', freetype_root_path)

        self.logger.info('Freetype: Copy include files')

        shutil.copytree('freetype/include', freetype_include_path)

        for build_type in self.args.build_types:
            self.logger.info('Freetype: Copy libraries for %s', build_type)

            original_suffix = 'd' if build_type == 'Debug' else ''
            suffix = '-d' if build_type == 'Debug' else ''

            if self.build_android or platform.system() == 'Linux':
                shutil.copy(os.path.join('freetype/build', build_type, 'libfreetype' + original_suffix + '.a'),              os.path.join(freetype_library_path, 'libfreetype' + suffix + '.a'))
            elif platform.system() == 'Windows':
                shutil.copy(os.path.join('freetype/build', build_type, build_type, 'freetype' + original_suffix + '.lib'),   os.path.join(freetype_library_path, 'freetype' + original_suffix + '.lib'))

                if build_type == 'Debug':
                    self.logger.info('Freetype: Copy pdb files')

                    for file in glob.glob(os.path.join('freetype/build', build_type, build_type, '*.pdb')):
                        shutil.copy(file, freetype_library_path)
            else:
                return False

        return True
