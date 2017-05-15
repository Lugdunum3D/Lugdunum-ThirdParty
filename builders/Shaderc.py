import os
import subprocess
import platform
import shutil

from git import Repo

class Shaderc():
    git_uri = "https://github.com/google/shaderc.git"

    def __init__(self, args, logger):
        self.args = args
        self.logger = logger

    def _clone(self):
        self.logger.info("Shaderc: Clone main repository")
        if not os.path.isdir("shaderc"):
            Repo.clone_from(Shaderc.git_uri, "shaderc")

        self.logger.info("Shaderc: Clone googletest repository")
        if not os.path.isdir("shaderc/third_party/googletest"):
            Repo.clone_from("https://github.com/google/googletest.git", "shaderc/third_party/googletest")

        self.logger.info("Shaderc: Clone glslang repository")
        if not os.path.isdir("shaderc/third_party/glslang"):
            Repo.clone_from("https://github.com/google/glslang.git", "shaderc/third_party/glslang")

        self.logger.info("Shaderc: Clone spirv-tools repository")
        if not os.path.isdir("shaderc/third_party/spirv-tools"):
            Repo.clone_from("https://github.com/KhronosGroup/SPIRV-Tools.git", "shaderc/third_party/spirv-tools")

        self.logger.info("Shaderc: Clone spirv-headers repository")
        if not os.path.isdir("shaderc/third_party/spirv-tools/external/spirv-headers"):
            Repo.clone_from("https://github.com/KhronosGroup/SPIRV-Headers.git", "shaderc/third_party/spirv-tools/external/spirv-headers")

        return True

    def _compile(self, build_type):
        self.logger.info("Shaderc: Configure for %s",  build_type)

        build_dir = os.path.join("shaderc/build", build_type)

        if not os.path.isdir(build_dir):
            os.makedirs(build_dir)

        cmake_args = [
            "cmake",
            "-DSHADERC_ENABLE_SHARED_CRT=ON",
            "-DENABLE_GLSLANG_BINARIES=OFF",
            "-DSHADERC_SKIP_TESTS=ON",
            "-DCMAKE_BUILD_TYPE=" + build_type,
            "-DCMAKE_POSITION_INDEPENDENT_CODE=ON",
            "../.."
        ]

        if subprocess.Popen(cmake_args, cwd=build_dir).wait():
             return False

        self.logger.info("Shaderc: Build for %s", build_type)
        if subprocess.Popen(["cmake", "--build", "."], cwd=build_dir).wait():
             return False

        return True

    def _copy_files(self):
        shaderc_root_path = os.path.join(self.args.path, "shaderc")
        shaderc_include_path = os.path.join(shaderc_root_path, "include")
        shaderc_library_path = os.path.join(shaderc_root_path, "lib")

        self.logger.info("Shaderc: Create directories")

        if not os.path.isdir(shaderc_include_path):
            os.makedirs(shaderc_include_path)

        if not os.path.isdir(shaderc_library_path):
            os.makedirs(shaderc_library_path)

        self.logger.info("Shaderc: Copy license file")

        shutil.copy("shaderc/LICENSE", shaderc_root_path)

        self.logger.info("Shaderc: Copy include files")

        real_include_path = os.path.join(shaderc_include_path, "shaderc")

        if not os.path.isdir(real_include_path):
            shutil.copytree("shaderc/libshaderc/include/shaderc", real_include_path)

        self.logger.info("Shaderc: Copy libraries")

        if platform.system() == "Linux":
            shutil.copy("shaderc/build/Debug/libshaderc/libshaderc_combined.a", os.path.join(shaderc_library_path, "libshaderc_combined-d.a"))
            shutil.copy("shaderc/build/Release/libshaderc/libshaderc_combined.a", os.path.join(shaderc_library_path, "libshaderc_combined.a"))
        elif platform.system() == "Windows":
            shutil.copy("shaderc/build/Debug/libshaderc/libshaderc_combined.a", os.path.join(shaderc_library_path, "shaderc_combined-d.lib"))
            shutil.copy("shaderc/build/Release/libshaderc/libshaderc_combined.a", os.path.join(shaderc_library_path, "shaderc_combined.lib"))
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
