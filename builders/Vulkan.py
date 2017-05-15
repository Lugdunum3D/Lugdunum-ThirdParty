import os
import shutil

from git import Repo

class Vulkan():
    git_uri = "https://github.com/KhronosGroup/Vulkan-Docs.git"

    def __init__(self, args, logger):
        self.args = args
        self.logger = logger

    def _clone(self):
        self.logger.info("Vulkan: Clone main repository")
        if not os.path.isdir("vulkan"):
            Repo.clone_from(Vulkan.git_uri, "vulkan")

        return True

    def _copy_files(self):
        vulkan_root_path = os.path.join(self.args.path, "vulkan")
        vulkan_include_path = os.path.join(vulkan_root_path, "include")

        self.logger.info("Vulkan: Create directories")

        if not os.path.isdir(vulkan_include_path):
            os.makedirs(vulkan_include_path)

        self.logger.info("Vulkan: Copy include files")

        real_include_path = os.path.join(vulkan_include_path, "vulkan")

        if not os.path.isdir(real_include_path):
            shutil.copytree("vulkan/src/vulkan", real_include_path)

        return True

    def build(self):
        if not self._clone():
            return False

        if not self._copy_files():
            return False

        return True
