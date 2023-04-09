import gazu
from .exceptions import *


class FileTree:

    def __init__(self, project: dict):
        """
        특정 project의 file_tree 정보에 접근하여 file_tree 정보를 수정하기 위한 class

        Args:
            project(dict): file_tree를 알아내고자 하는 대상 project의 dict
        """
        self.project = project
        self.project_name = project.get('name')
        self.file_tree = project.get('file_tree')
        self._mnt_point = None
        self._root = None
        self._style = None
        self._working_shot_file_path = None
        self._working_asset_file_path = None
        self._working_shot_file_name = None
        self._working_asset_file_name = None
        self._output_shot_file_path = None
        self._output_asset_file_path = None
        self._output_shot_file_name = None
        self._output_asset_file_name = None

        self.init_file_tree()

    @property
    def mnt_point(self):
        """
        Returns:
            dict: mount point path for output and working files.
        """
        return self._mnt_point

    @mnt_point.setter
    def mnt_point(self, value):
        """
        Args:
            value(dict): mount point path for output and working files.
        """
        self._mnt_point = value

    @property
    def root(self):
        """
        Returns:
            dict: root path for output and working files.
        """
        return self._root

    @root.setter
    def root(self, value):
        """
        Args:
            value(dict): root path for output and working files.
        """
        self._root = value

    @property
    def style(self):
        """
        Returns:
            dict: style for output and working files.
        """
        return self._style

    @style.setter
    def style(self, value):
        """
        Args:
            value(dict): style for output and working files.
        """
        self._style = value

    @property
    def working_shot_file_path(self):
        """
        Returns:
            dict: shot file path for working files.
        """
        return self._working_shot_file_path

    @working_shot_file_path.setter
    def working_shot_file_path(self, value):
        """
        Args:
            value(dict): shot file path for working files.
        """
        self._working_shot_file_path = value

    @property
    def working_asset_file_path(self):
        """
        Returns:
            dict: asset file path for working files.
        """
        return self._working_asset_file_path

    @working_asset_file_path.setter
    def working_asset_file_path(self, value):
        """
        Args:
            value(dict): asset file path for working files.
        """
        self._working_asset_file_path = value

    @property
    def working_shot_file_name(self):
        """
        Returns:
            dict: shot file name for working files.
        """
        return self._working_shot_file_name

    @working_shot_file_name.setter
    def working_shot_file_name(self, value):
        """
        Args:
            value(dict): shot file name for working files.
        """
        self._working_shot_file_name = value

    @property
    def working_asset_file_name(self):
        """
        Returns:
            dict: asset file name for working files.
        """
        return self._working_asset_file_name

    @working_asset_file_name.setter
    def working_asset_file_name(self, value):
        """
        Args:
            value(dict): asset file name for working files.
        """
        self._working_asset_file_name = value

    @property
    def output_shot_file_path(self):
        """
        Returns:
            dict: shot file path for output files.
        """
        return self._output_shot_file_path

    @output_shot_file_path.setter
    def output_shot_file_path(self, value):
        """
        Args:
            value(dict): shot file path for output files.
        """
        self._output_shot_file_path = value

    @property
    def output_asset_file_path(self):
        """
        Returns:
            dict: asset file path for output files.
        """
        return self._output_asset_file_path

    @output_asset_file_path.setter
    def output_asset_file_path(self, value):
        """
        Args:
            value(dict): asset file path for output files.
        """
        self._output_asset_file_path = value

    @property
    def output_shot_file_name(self):
        """
        Returns:
            dict: shot file name for output files.
        """
        return self._output_shot_file_name

    @output_shot_file_name.setter
    def output_shot_file_name(self, value):
        """
        Args:
            value(dict): shot file name for output files.
        """
        self._output_shot_file_name = value

    @property
    def output_asset_file_name(self):
        """
        Returns:
            dict: asset file name for output files.
        """
        return self._output_asset_file_name

    @output_asset_file_name.setter
    def output_asset_file_name(self, value):
        """
        Args:
            value(dict): asset file name for output files.
        """
        self._output_asset_file_name = value

    def init_file_tree(self):
        """
        file_tree를 참조하여 객체 변수에 반영하고
        file_tree값이 None이면 update_file_tree의 file_tree(dict) value값을 None으로 return.
        file_tree값이 dict가 아니면 update_file_tree의 file_tree(dict) value값을 빈 dict를 return
        """
        if not self.file_tree:
            return self.update_file_tree()

        elif not isinstance(self.file_tree, dict):
            raise DictTypeError("Type error")

        self.mnt_point = self.file_tree.get('working', {}).get('mountpoint')
        self._root = self.file_tree.get('working', {}).get('root')
        self._style = self.file_tree.get('working', {}).get('folder_path', {}).get('style')
        self._working_shot_file_path = self.file_tree.get('working', {}).get('folder_path', {}).get('shot')
        self._working_asset_file_path = self.file_tree.get('working', {}).get('folder_path', {}).get('asset')
        self._working_shot_file_name = self.file_tree.get('working', {}).get('file_name', {}).get('shot')
        self._working_asset_file_name = self.file_tree.get('working', {}).get('file_name', {}).get('asset')
        self._output_shot_file_path = self.file_tree.get('output', {}).get('folder_path', {}).get('shot')
        self._output_asset_file_path = self.file_tree.get('output', {}).get('folder_path', {}).get('asset')
        self._output_shot_file_name = self.file_tree.get('output', {}).get('file_name', {}).get('shot')
        self._output_asset_file_name = self.file_tree.get('output', {}).get('file_name', {}).get('asset')

    def update_file_tree(self):
        """
        file_tree안에 들어가는 path정보를 담은 객체변수를 dict형태로 조합하고 반영
        """
        file_tree = {
            "working": {
                "mountpoint": self.mnt_point,
                "root": self._root,
                "folder_path": {
                    "shot": self._working_shot_file_path,
                    "asset": self._working_asset_file_path,
                    "style": self._style
                },
                "file_name": {
                    "shot": self._working_shot_file_name,
                    "asset": self._working_asset_file_name,
                    "style": self._style
                }
            },
            "output": {
                "mountpoint": self._mnt_point,
                "root": self._root,
                "folder_path": {
                    "shot": self._output_shot_file_path,
                    "asset": self._output_asset_file_path,
                    "style": self._style
                },
                "file_name": {
                    "shot": self._output_shot_file_name,
                    "asset": self._output_asset_file_name,
                    "style": self._style
                }
            }
        }
        gazu.files.update_project_file_tree(self.project, file_tree)
