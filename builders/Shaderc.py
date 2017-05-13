import os
import subprocess
import platform
import shutil

from git import Repo

class Shaderc():
    git_uri = "https://github.com/google/shaderc.git"

    def __init__(self, args):
        self.args = args

    def _clone(self):
        print(" -- Shaderc: Clone Shaderc main repository")
        if os.path.isdir("shaderc"):
            self.repo = Repo("shaderc")
        else:
            self.repo = Repo.clone_from(Shaderc.git_uri, "shaderc")

        print(" -- Shaderc: Clone googletest repository")
        if os.path.isdir("shaderc/third_party/googletest"):
            self.googletest_repo = Repo("shaderc/third_party/googletest")
        else:
            self.googletest_repo = Repo.clone_from("https://github.com/google/googletest.git", "shaderc/third_party/googletest")

        print(" -- Shaderc: Clone glslang repository")
        if os.path.isdir("shaderc/third_party/glslang"):
            self.glslang_repo = Repo("shaderc/third_party/glslang")
        else:
            self.glslang_repo = Repo.clone_from("https://github.com/google/glslang.git", "shaderc/third_party/glslang")

        print(" -- Shaderc: Clone spirv-tools repository")
        if os.path.isdir("shaderc/third_party/spirv-tools"):
            self.spirv_tools_repo = Repo("shaderc/third_party/spirv-tools")
        else:
            self.spirv_tools_repo = Repo.clone_from("https://github.com/KhronosGroup/SPIRV-Tools.git", "shaderc/third_party/spirv-tools")

        print(" -- Shaderc: Clone spirv-headers repository")
        if os.path.isdir("shaderc/third_party/spirv-tools/external/spirv-headers"):
            self.spirv_headers_repo = Repo("shaderc/third_party/spirv-tools/external/spirv-headers")
        else:
            self.spirv_headers_repo = Repo.clone_from("https://github.com/KhronosGroup/SPIRV-Headers.git", "shaderc/third_party/spirv-tools/external/spirv-headers")

        return True

    def _compile(self):
        print(" -- Shaderc: Configure")

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

        print(" -- Shaderc: Build")
        if subprocess.Popen(["cmake", "--build", "."], cwd="shaderc/build").wait():
             return False

        return True

    def build(self):
        if not self._clone():
            return False

        if not self._compile():
            return False

        return True

    def copy_files(self):
        shaderc_root_path = os.path.join(self.args.path, "shaderc")
        shaderc_include_path = os.path.join(shaderc_root_path, "include")
        shaderc_library_path = os.path.join(shaderc_root_path, "lib")

        print(" -- Shaderc: Create directories")

        if not os.path.isdir(shaderc_root_path):
            os.mkdir(shaderc_root_path)

        if not os.path.isdir(shaderc_include_path):
            os.mkdir(shaderc_include_path)

        if not os.path.isdir(shaderc_library_path):
            os.mkdir(shaderc_library_path)

        print(" -- Shaderc: Copy include files")

        real_include_path = os.path.join(shaderc_include_path, "shaderc")

        if not os.path.isdir(real_include_path):
            shutil.copytree("shaderc/libshaderc/include/shaderc", real_include_path)

        print(" -- Shaderc: Copy library")

        if platform.system() == "Linux":
            library_file = "shaderc/build/libshaderc/libshaderc_combined.a"
        elif platform.system() == "Windows":
            library_file = "shaderc/build/libshaderc/shaderc_combined.lib"
        else:
            return False


        shutil.copy(library_file, shaderc_library_path)

        return True
