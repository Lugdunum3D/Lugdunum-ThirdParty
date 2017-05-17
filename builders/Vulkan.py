import os
import shutil

from git import Repo

from .Builder import Builder

# Possible configuration
#   repository.uri (optional) => The uri of the git repository to clone
#   repository.tag (mandatory) => The tag to checkout to before building

class Vulkan(Builder):
    default_repository_uri = "https://github.com/KhronosGroup/Vulkan-Docs.git"

    def _clone(self):
        self.logger.info("Vulkan: Clone main repository")

        repo = None
        if not os.path.isdir("vulkan"):
            repo = Repo.clone_from(self.config["repository"]["uri"], "vulkan")
        else:
            repo = Repo("vulkan")

        repo.git.checkout(self.config["repository"]["tag"])

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
