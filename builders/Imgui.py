import os
import shutil

from git import Repo

from .Builder import Builder

# Possible configuration
#   repository.uri (optional) => The uri of the git repository to clone
#   repository.tag (mandatory) => The tag to checkout to before building

class Imgui(Builder):
    default_repository_uri = 'https://github.com/ocornut/imgui.git'

    def _clone(self):
        self.logger.info('Imgui: Clone main repository')

        repo = None
        if not os.path.isdir('imgui'):
            repo = Repo.clone_from(self.config['repository']['uri'], 'imgui')
        else:
            repo = Repo('imgui')

        repo.remotes['origin'].fetch()
        repo.git.checkout(self.config['repository']['tag'])

        return True

    def _copy_files(self):
        imgui_root_path = os.path.join(self.args.path, 'imgui')
        imgui_include_path = os.path.join(imgui_root_path, 'include')
        imgui_src_path = os.path.join(imgui_root_path, 'src')

        self.logger.info('Imgui: Create directories')

        if not os.path.isdir(imgui_include_path):
            os.makedirs(imgui_include_path)

        if not os.path.isdir(imgui_src_path):
            os.makedirs(imgui_src_path)

        self.logger.info('Imgui: Copy license file')

        shutil.copy('imgui/LICENSE', imgui_root_path)

        self.logger.info('Imgui: Copy include files')

        shutil.copy(os.path.join(os.path.dirname(os.path.realpath(__file__)), "../assets/imgui/include/imconfig.h"), imgui_include_path)
        shutil.copy('imgui/imgui.h', imgui_include_path)
        shutil.copy('imgui/imgui_internal.h', imgui_include_path)
        shutil.copy('imgui/stb_rect_pack.h', imgui_include_path)
        shutil.copy('imgui/stb_textedit.h', imgui_include_path)
        shutil.copy('imgui/stb_truetype.h', imgui_include_path)

        self.logger.info('Imgui: Copy src files')

        shutil.copy('imgui/imgui.cpp', imgui_src_path)
        shutil.copy('imgui/imgui_demo.cpp', imgui_src_path)
        shutil.copy('imgui/imgui_draw.cpp', imgui_src_path)

        return True
