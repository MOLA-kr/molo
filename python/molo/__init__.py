"""
MOLO is a shot-load API for compositing artists who use NUKE.
This API uses gazu API to get data from Kitsu database.



**How to use MOLO API**


1) Login:
    To receive shot data assigned to the user, MOLO requires access to Kitsu.
    Use the Auth object to create a connection with Kitsu and authenticate the user.
    
    Before using all other MOLO API modules, an Auth object must be created.
    The connect_host and log_in methods try to connect with the entered argument values.

    Example usage:
    >>> my_auth = Auth()
    >>> my_auth.connect_host("{HOST URL}")
    >>> my_auth.log_in("{USER ID}", "{USER PASSWORD}")

    Once connected, MOLO automatically connects when an Auth object is created.
    >>> my_auth = Auth()

    The local user information is saved in the '~/.config/Molo/user.json' file.
    When logout is executed, the contents are reset and exit from automatic login mode.
    >>> my_auth.log_out()


2) Task Browsing:
    Use the TaskBrowser module to search for shot informaition assigned to the user.
    The 'task' indicates 'comp task' in this module.
    User can sort the shots using the 'Sort_by' function and the criteria specified by the 'key' parameter.

    The shot information user can receive is:
    --> info = ['name', 'project_name', 'entity_name', 'sequence_name',
            'task_type_name', 'task_status_name', 'due_date', 'priority']

    --> Example Criterion:
                'due_date', 'start_date', 'updated_at', 'created_at', 'last_comment_date' etc

    Example usage:
    >>> browser = TaskBrowser()
    >>> sorted_by_duedate = browser.sorted_by_due_date


3) Get Task information from Comptask:
    Use the CompTask module to get information about tasks with a shot as an entity.
    --> information = ['project_name', 'sequence_name', 'shot_name', 'project_id', 'sequence_id', 'shot_id', 
                        'fps', 'ratio', 'resolution', 'frame_in', 'frame_out', 'task_status']

    Example usage:
    >>> browser = TaskBrowser()
    >>> comp_tasks = browser.sorted_by_due_date
    >>> CompTask(comp_tasks[{INDEX_NUM}])


4) Loader:
    Open a selected task's Nuke file with the last version.
    If the working file does not exist, it creates a new '.nk' file.
    To use, the loader needs a selected task to create a working file and returns a working file as a dictionary,
    which can be used later when creating an output file.

    Example usage:
    >>> browser = TaskBrowser()
    >>> comp_tasks = browser.sorted_by_due_date
    >>> selected_task = CompTask(comp_tasks[0])
    >>> load = Loader()
    >>> load.open_nuke_working_file(selected_task)


5) Nuke Function:
    This module contains Nuke-related functions that can be summarized into four main categories:
    setting the project, creating nodes, updating nodes, and saving/opening Nuke script.

    5-1) Set Project:
        Gets the frame in, frame out, resolution, and fps information from the selected comp task and
        changes the project settings of the current Nuke script using this information.

    5-2) Create Nodes:
        Creates constant node, merge node.
        Creates Camera nodes and Read nodes for each of the output files.
        Sets the back node to indicate the type of the nodes,
        and calculates the coordinates of the node and the range of positions placed on the node graph as rectangles.
        The calculation is used to make the nodes seperated and not overlapped.

    5-3) Update Nodes:
        Finds the node by using task type name
        and compares the task type of all the nodes openned in the current Nuke script.
        If the task type is the same but the path and ID are different, it replaces the path and ID

    5-4) Save / Open Nuke Script:
        Uses 'self.working_file_path' to save new Nuke script.
        Clears the currently opened Nuke script and opens the Nuke script with the selected 'self.working_file_path'.
        If the script has been modified,
        it checks whether that selected Nuke script has already been saved before processing.


6) Filetree:
    This module accesses to the information of file_tree from selected project. 
    Shows original information of the filetree, and user can change the pattern of the filetree.
    If the file_tree value is None, return None.
    If the file_tree value is not dictionary, return empty dictionary.

    Example usage:
    >>> project = gazu.project.get_project_by_name("{PROJECT NAME}")
    >>> tree = FileTree(project)
    
            tree.mnt_point = '{NEW MNT POINT}'
            tree.root = '{NEW ROOT}'
            tree.style = '{NEW STYLE}'
            tree.working_shot_file_path = '{NEW SHOT FILE PATH}'
            tree.working_asset_file_path = '{NEW ASSET FILE PATH}'
            tree.working_shot_file_name = '{NEW SHOT FILE NAME}'
            tree.working_asset_file_name = '{NEW ASSET FILE NAME}'
            tree.output_shot_file_path = '{NEW SHOT FILE PATH}'
            tree.output_asset_file_path = '{NEW ASSET FILE PATH}'
            tree.output_shot_file_name = '{NEW SHOT FILE NAME}'
    
    >>> tree.update_file_tree()


7) Log:
    Create a log file and leave a record by log message.
    You can find the log file that named 'molo_test.log' on '~/.config/Molo/'.

    *log message for*
    --> information of host_url
    --> login access
    --> output file load success or fail
    --> Nuke file create success or fail



**How to use MOLO Widget**


 MOLO Widget is a graphical user interface built on to of the MOLO API, using Pyside2.

 MOLO Widget contains three widgets: the Main Widget, the Login Widget, and the Host Widget.
 The 'Login Widget' allows users to input their ID and password, while the Host Widget provides a field for the user
 to enter the host URL. The "Remember Me" feature saves user information in JSON format,
 which is stored locally in the ".config" directory.
 The 'Main widget' contains all the other main functions.


1) Main Widget:
    1-1) User Button:
        Displays information about the currently logged-in user and provided a logout function.
        Connected to the 'molo_user_frame.py' module.

    1-2) Task Tree:
        Displays a tree of the tasks and can be used as a search engine for the shots.

    1-3) Reload Button:
        Reloads the list of compositing tasks assigned to the currently logged-in user.

    1-4) Task Browser:
        Displays information about shots assigned to the user,
        including thumbnails, project name, sequence name, and shot name.
        Users can sort shots using criteria set in the QComboBox.
        The default criterion is the order of the shots, with options to sort shots by 'Due date' and 'Priority'.
        Selecting a shot thumbnail displays additional information in the sidebar.

    1-5) Side Thumbnail:
        Displays detailed information about the selected shot,
        including Project name, Sequence name, Shot name, Frame Range, Resolution, FPS, and Revision.

    1-6) Comment Box:
        Displays comments related to the selected compositiong task.

    1-7) Task Table Browser:
        Displays data related to the output file of other tasks required by the compositor,
        including Task Type, Status, Version, Extension, and Updated date.
        Version information is marked using icons.
        All rows are selected by default, but users can select or deselect items by clicking on them.
        The reload task table browser button('🔄') allows users to refresh the table.

    1-8) Open / Load in Nuke:
        When no node is set and the current Nuke file is 'untitled', the button shows 'Open in Nuke'.
        Clicking it creates or opens the working file of the selected task.

        When a certain shot and nodes are already set, the button shows 'Load Selected Files'.
        Clicking it creates or updates the nodes of the selected output files.


2) MVC:
    2-1) Task Table Model:
        Displays data related to the output files of other tasks required by the compositor.

    2-2) Task Browser Model:
        Displays tasks assigned to the Compositor ana marks them as current status.
        The tooltip shows due date and priority.


3) MOLO Panel:
    To use MOLO Panel in Nuke:
        '~/.nuke/menu.py' :
        # IMPORT PANEL EXAMPLE
        >>> from nukescripts import panels
        >>> from molo_main_panel import MoloWidget
        >>> panels.registerWidgetAsPanel('MoloWidget', 'MOLO Panel', 'molo_panel.molo')
    
"""

from molo.auth import Auth
from molo.comptask import CompTask
from molo.exceptions import MoloException
from molo.filetree import FileTree
from molo.loader import Loader
from molo.taskbrowser import TaskBrowser
from molo.utils import print_align, print_info, user_info_tree, construct_full_path, construct_initials
from molo.logger import Logger
from molo import PySide

__all__ = ["Auth", "CompTask", "MoloException", "FileTree", "Loader", "TaskBrowser",
           "Logger", "print_align", "print_info", "construct_full_path"]
