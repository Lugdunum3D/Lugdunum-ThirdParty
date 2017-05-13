import os
import subprocess
import platform
import shutil

from git import Repo

class Shaderc():
    git_uri = "https://github.com/google/shaderc.git"

    def __init__(self, args, logger):
        self.args = args
        self.logger = logger;

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

    def _compile(self):
        self.logger.info("Shaderc: Configure")

        if not os.path.isdir("shaderc/build"):
            os.mkdir("shaderc/build")

        cmake_args = [
            "cmake",
            "-DSHADERC_ENABLE_SHARED_CRT=ON",
            "-DENABLE_HLSL=OFF",
            "-DENABLE_GLSLANG_BINARIES=OFF",
            "-DSHADERC_SKIP_TESTS=ON",
            "-DCMAKE_BUILD_TYPE=" + self.args.build_type,
            "-DCMAKE_POSITION_INDEPENDENT_CODE=ON",
            ".."
        ]

        if subprocess.Popen(cmake_args, cwd="shaderc/build").wait():
             return False

        self.logger.info("Shaderc: Build")
        if subprocess.Popen(["cmake", "--build", "."], cwd="shaderc/build").wait():
             return False

        return True

    def _copy_files(self):
        shaderc_root_path = os.path.join(self.args.path, "shaderc")
        shaderc_include_path = os.path.join(shaderc_root_path, "include")
        shaderc_library_path = os.path.join(shaderc_root_path, "lib")

        self.logger.info("Shaderc: Create directories")

        if not os.path.isdir(shaderc_root_path):
            os.mkdir(shaderc_root_path)

        if not os.path.isdir(shaderc_include_path):
            os.mkdir(shaderc_include_path)

        if not os.path.isdir(shaderc_library_path):
            os.mkdir(shaderc_library_path)

        self.logger.info("Shaderc: Copy include files")

        real_include_path = os.path.join(shaderc_include_path, "shaderc")

        if not os.path.isdir(real_include_path):
            shutil.copytree("shaderc/libshaderc/include/shaderc", real_include_path)

        self.logger.info("Shaderc: Copy library")

        if platform.system() == "Linux":
            library_file = "shaderc/build/libshaderc/libshaderc_combined.a"
        elif platform.system() == "Windows":
            library_file = "shaderc/build/libshaderc/shaderc_combined.lib"
        else:
            return False

        shutil.copy(library_file, shaderc_library_path)

        return True

    def build(self):
        if not self._clone():
            return False

        if not self._compile():
            return False

        if not self._copy_files():
            return False

        return True
