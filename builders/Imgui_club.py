import os
import shutil

from git import Repo

from .Builder import Builder

# Possible configuration
#   repository.uri (optional) => The uri of the git repository to clone
#   repository.tag (mandatory) => The tag to checkout to before building

class Imgui_club(Builder):
    default_repository_uri = 'https://github.com/ocornut/Imgui_club.git'

    def _clone(self):
        self.logger.info('Imgui_club: Clone main repository')

        repo = None
        if not os.path.isdir('imgui_club'):
            repo = Repo.clone_from(self.config['repository']['uri'], 'imgui_club')
        else:
            repo = Repo('imgui_club')

        repo.remotes['origin'].fetch()
        repo.git.checkout(self.config['repository']['tag'])

        return True

    def _copy_files(self):
        imgui_club_root_path = os.path.join(self.args.path, 'imgui_club')
        imgui_club_include_path = os.path.join(imgui_club_root_path, 'include')
        imgui_club_src_path = os.path.join(imgui_club_root_path, 'src')

        self.logger.info('Imgui_club: Create directories')

        if not os.path.isdir(imgui_club_include_path):
            os.makedirs(imgui_club_include_path)

        if not os.path.isdir(imgui_club_src_path):
            os.makedirs(imgui_club_src_path)

        self.logger.info('Imgui_club: Copy include files')

        shutil.copy('imgui_club/imgui_freetype/imgui_freetype.h', imgui_club_include_path)

        self.logger.info('Imgui_club: Copy src files')

        shutil.copy('imgui_club/imgui_freetype/imgui_freetype.cpp', imgui_club_src_path)

        return True
