import os
import subprocess
import platform
import shutil

from git import Repo

class GoogleMock():
    git_uri = "https://github.com/google/googletest.git"

    def __init__(self, args, logger):
        self.args = args
        self.logger = logger

    def _clone(self):
        self.logger.info("GoogleMock: Clone main repository")
        if not os.path.isdir("googletest"):
            Repo.clone_from(GoogleMock.git_uri, "googletest")

        return True

    def _compile(self, build_type):
        self.logger.info("GoogleMock: Configure for %s",  build_type)

        build_dir = os.path.join("googletest/build", build_type)

        if not os.path.isdir(build_dir):
            os.makedirs(build_dir)

        cmake_args = [
            "cmake",
            "-DCMAKE_BUILD_TYPE=" + build_type,
            "../.."
        ]

        if subprocess.Popen(cmake_args, cwd=build_dir).wait():
             return False

        self.logger.info("GoogleMock: Build for %s", build_type)
        if subprocess.Popen(["cmake", "--build", "."], cwd=build_dir).wait():
             return False

        return True

    def _copy_files(self):
        googlemock_root_path = os.path.join(self.args.path, "googlemock")
        googlemock_include_path = os.path.join(googlemock_root_path, "include")
        googlemock_library_path = os.path.join(googlemock_root_path, "lib")

        self.logger.info("GoogleMock: Create directories")

        if not os.path.isdir(googlemock_include_path):
            os.makedirs(googlemock_include_path)

        if not os.path.isdir(googlemock_library_path):
            os.makedirs(googlemock_library_path)

        self.logger.info("GoogleMock: Copy license file")

        shutil.copy("googletest/googlemock/LICENSE", googlemock_root_path)

        self.logger.info("GoogleMock: Copy include files")

        gmock_real_include_path = os.path.join(googlemock_include_path, "gmock")

        if not os.path.isdir(gmock_real_include_path):
            shutil.copytree("googletest/googlemock/include/gmock", gmock_real_include_path)

        gtest_real_include_path = os.path.join(googlemock_include_path, "gtest")

        if not os.path.isdir(gtest_real_include_path):
            shutil.copytree("googletest/googletest/include/gtest", gtest_real_include_path)

        self.logger.info("GoogleMock: Copy libraries")

        if platform.system() == "Linux":
            shutil.copy("googletest/build/Debug/googlemock/gtest/libgtest.a", os.path.join(googlemock_library_path, "libgtestd.a"))
            shutil.copy("googletest/build/Release/googlemock/gtest/libgtest.a", os.path.join(googlemock_library_path, "libgtest.a"))

            shutil.copy("googletest/build/Debug/googlemock/gtest/libgtest_main.a", os.path.join(googlemock_library_path, "libgtest_maind.a"))
            shutil.copy("googletest/build/Release/googlemock/gtest/libgtest_main.a", os.path.join(googlemock_library_path, "libgtest_main.a"))

            shutil.copy("googletest/build/Debug/googlemock/libgmock.a", os.path.join(googlemock_library_path, "libgmockd.a"))
            shutil.copy("googletest/build/Release/googlemock/libgmock.a", os.path.join(googlemock_library_path, "libgmock.a"))

            shutil.copy("googletest/build/Debug/googlemock/libgmock_main.a", os.path.join(googlemock_library_path, "libgmock_maind.a"))
            shutil.copy("googletest/build/Release/googlemock/libgmock_main.a", os.path.join(googlemock_library_path, "libgmock_main.a"))
        elif platform.system() == "Windows":
            shutil.copy("googletest/build/Debug/googlemock/gtest/gtest.lib", os.path.join(googlemock_library_path, "gtestd.lib"))
            shutil.copy("googletest/build/Release/googlemock/gtest/gtest.lib", os.path.join(googlemock_library_path, "gtest.lib"))

            shutil.copy("googletest/build/Debug/googlemock/gtest/gtest_main.lib", os.path.join(googlemock_library_path, "gtest_maind.lib"))
            shutil.copy("googletest/build/Release/googlemock/gtest/gtest_main.lib", os.path.join(googlemock_library_path, "gtest_main.lib"))

            shutil.copy("googletest/build/Debug/googlemock/gmock.lib", os.path.join(googlemock_library_path, "gmockd.lib"))
            shutil.copy("googletest/build/Release/googlemock/gmock.lib", os.path.join(googlemock_library_path, "gmock.lib"))

            shutil.copy("googletest/build/Debug/googlemock/gmock_main.lib", os.path.join(googlemock_library_path, "gmock_maind.lib"))
            shutil.copy("googletest/build/Release/googlemock/gmock_main.lib", os.path.join(googlemock_library_path, "gmock_main.lib"))
        else:
            return False

        return True

    def build(self):
        if not self._clone():
            return False

        if not self._compile("Debug"):
            return False

        if not self._compile("Release"):
            return False

        if not self._copy_files():
            return False

        return True
