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

    def _clone(self, tag):
        self.logger.info("GoogleMock: Clone main repository")

        repo = None
        if not os.path.isdir("googletest"):
            repo = Repo.clone_from(GoogleMock.git_uri, "googletest")
        else:
            repo = Repo("googletest")

        repo.git.checkout(tag)

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
        if subprocess.Popen(["cmake", "--build", ".", "--config", build_type], cwd=build_dir).wait():
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

        for build_type in self.args.build_types:
            self.logger.info("GoogleMock: Copy libraries %s", build_type)

            suffix = "d" if build_type == "Debug" else ""

            if platform.system() == "Linux":
                shutil.copy("googletest/build/" + build_type + "/googlemock/gtest/libgtest.a", os.path.join(googlemock_library_path, "libgtest" + suffix + ".a"))
                shutil.copy("googletest/build/" + build_type + "/googlemock/gtest/libgtest_main.a", os.path.join(googlemock_library_path, "libgtest_main" + suffix + ".a"))
                shutil.copy("googletest/build/" + build_type + "/googlemock/libgmock.a", os.path.join(googlemock_library_path, "libgmock" + suffix + ".a"))
                shutil.copy("googletest/build/" + build_type + "/googlemock/libgmock_main.a", os.path.join(googlemock_library_path, "libgmock_main" + suffix + ".a"))
            elif platform.system() == "Windows":
                shutil.copy("googletest/build/" + build_type + "/googlemock/gtest/" + build_type + "/gtest.lib", os.path.join(googlemock_library_path, "gtest" + suffix + ".lib"))
                shutil.copy("googletest/build/" + build_type + "/googlemock/gtest/" + build_type + "/gtest_main.lib", os.path.join(googlemock_library_path, "gtest_main" + suffix + ".lib"))
                shutil.copy("googletest/build/" + build_type + "/googlemock/" + build_type + "/gmock.lib", os.path.join(googlemock_library_path, "gmock" + suffix + ".lib"))
                shutil.copy("googletest/build/" + build_type + "/googlemock/" + build_type + "/gmock_main.lib", os.path.join(googlemock_library_path, "gmock_main" + suffix + ".lib"))
            else:
                return False

        return True

    def build(self, tag="master"):
        if not self._clone(tag):
            return False

        for build_type in self.args.build_types:
            if not self._compile(build_type):
                return False

        if not self._copy_files():
            return False

        return True
