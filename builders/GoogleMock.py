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

class GoogleMock(Builder):
    default_repository_uri = 'https://github.com/google/googletest.git'

    def _clone(self):
        self.logger.info('GoogleMock: Clone main repository')

        repo = None
        if not os.path.isdir('googletest'):
            repo = Repo.clone_from(self.config['repository']['uri'], 'googletest')
        else:
            repo = Repo('googletest')

        repo.remotes['origin'].fetch()
        repo.git.checkout(self.config['repository']['tag'])

        return True

    def _compile(self, build_type):
        self.logger.info('GoogleMock: Configure for %s',  build_type)

        build_dir = os.path.join('googletest/build', build_type)

        if not os.path.isdir(build_dir):
            os.makedirs(build_dir)

        cmake_args = [
            'cmake',
            '-DCMAKE_BUILD_TYPE=' + build_type,
            '-DCMAKE_POSITION_INDEPENDENT_CODE=ON',
            '-Dgtest_force_shared_crt=ON',
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

        self.logger.info('GoogleMock: Build for %s', build_type)
        if subprocess.Popen(['cmake', '--build', '.', '--config', build_type], cwd=build_dir).wait():
             return False

        return True

    def _copy_files(self):
        googlemock_root_path = os.path.join(self.args.path, 'googlemock')
        googlemock_include_path = os.path.join(googlemock_root_path, 'include')
        googlemock_library_path = os.path.join(googlemock_root_path, 'lib')

        self.logger.info('GoogleMock: Create directories')

        if not os.path.isdir(googlemock_include_path):
            os.makedirs(googlemock_include_path)

        if not os.path.isdir(googlemock_library_path):
            os.makedirs(googlemock_library_path)

        self.logger.info('GoogleMock: Copy license file')

        shutil.copy('googletest/googlemock/LICENSE', googlemock_root_path)

        self.logger.info('GoogleMock: Copy include files')

        gmock_real_include_path = os.path.join(googlemock_include_path, 'gmock')

        if not os.path.isdir(gmock_real_include_path):
            shutil.copytree('googletest/googlemock/include/gmock', gmock_real_include_path)

        gtest_real_include_path = os.path.join(googlemock_include_path, 'gtest')

        if not os.path.isdir(gtest_real_include_path):
            shutil.copytree('googletest/googletest/include/gtest', gtest_real_include_path)

        for build_type in self.args.build_types:
            self.logger.info('GoogleMock: Copy libraries %s', build_type)

            suffix = 'd' if build_type == 'Debug' else ''

            if self.build_android or platform.system() == 'Linux':
                shutil.copy(os.path.join('googletest/build', build_type, 'googlemock/gtest/libgtest.a'),                    os.path.join(googlemock_library_path, 'libgtest' + suffix + '.a'))
                shutil.copy(os.path.join('googletest/build', build_type, 'googlemock/gtest/libgtest_main.a'),               os.path.join(googlemock_library_path, 'libgtest_main' + suffix + '.a'))
                shutil.copy(os.path.join('googletest/build', build_type, 'googlemock/libgmock.a'),                          os.path.join(googlemock_library_path, 'libgmock' + suffix + '.a'))
                shutil.copy(os.path.join('googletest/build', build_type, 'googlemock/libgmock_main.a'),                     os.path.join(googlemock_library_path, 'libgmock_main' + suffix + '.a'))
            elif platform.system() == 'Windows':
                shutil.copy(os.path.join('googletest/build', build_type, 'googlemock/gtest', build_type, 'gtest.lib'),      os.path.join(googlemock_library_path, 'gtest' + suffix + '.lib'))
                shutil.copy(os.path.join('googletest/build', build_type, 'googlemock/gtest', build_type, 'gtest_main.lib'), os.path.join(googlemock_library_path, 'gtest_main' + suffix + '.lib'))
                shutil.copy(os.path.join('googletest/build', build_type, 'googlemock', build_type, 'gmock.lib'),            os.path.join(googlemock_library_path, 'gmock' + suffix + '.lib'))
                shutil.copy(os.path.join('googletest/build', build_type, 'googlemock', build_type, 'gmock_main.lib'),       os.path.join(googlemock_library_path, 'gmock_main' + suffix + '.lib'))

                if build_type == 'Debug':
                    self.logger.info('GoogleMock: Copy pdb files')

                    for file in glob.glob(os.path.join('googletest/build', build_type, 'googlemock/gtest', build_type, '*.pdb')):
                        shutil.copy(file, googlemock_library_path)

                    for file in glob.glob(os.path.join('googletest/build', build_type, 'googlemock', build_type, '*.pdb')):
                        shutil.copy(file, googlemock_library_path)
            else:
                return False

        return True
