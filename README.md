![MOLO_ICON](https://user-images.githubusercontent.com/122800378/230761283-a09ac809-43b8-4444-b7b7-85b1b5c461fc.png)


# What is MOLO

MOLO is a shot-load API for compositing artists who use NUKE.

This API uses [Gazu API](https://github.com/cgwire/gazu) to get data from [Kitsu](https://github.com/cgwire/kitsu) database.

# **How to use MOLO API**

## Login

In order to receive the data of the shots, which user will start to work on, access to Kitsu is required.

MOLO allows workers to login to the host and record information in the local environment.

Before using all other MOLO API modules, an Auth object must be created.

The connect_host and log_in methods try to connect with the entered argument values.

```python
my_auth = Auth()
my_auth.connect_host("{HOST URL}")
my_auth.log_in("{USER ID}", "{USER PASSWORD}")
```

Once connected, it automatically connects when an Auth object is created.

```python
my_auth = Auth()
```

Local records are saved in '`~/.config/Molo/user.json`'.

When logout is executed, the contents are reset and exit from automatic login mode.

```python
my_auth.log_out()
```

## Task Browsing

This is a module in which the user can search for shot information assigned to the user self.

The 'task' indicates 'comp task' in this module.

The shot information user can receive is:

> info = ['name', 'project_name', 'entity_name', 'sequence_name', 'task_type_name', 'task_status_name', 'due_date', 'priority']
> 

User can use 'Sort_by' function to list up the comp task list using specific criteria.

Criterion is the key value which becomes a criteria of order of the list.

> Example Criterion: 'due_date', 'start_date', 'updated_at', 'created_at', 'last_comment_date' etc
> 

```python
browser = TaskBrowser()
sorted_by_duedate = browser.sorted_by_due_date
```

## Get Task information from Comptask

Get information about tasks with shot as entity.

> information = ['project_name', 'sequence_name', 'shot_name', 'project_id', 'sequence_id', 'shot_id', 'fps', 'ratio', 'resolution', 'frame_in', 'frame_out', 'task_status']
> 

```python
browser = TaskBrowser()
comp_tasks = browser.sorted_by_due_date
CompTask(comp_tasks[{INDEX_NUM}])
```

## Load

Open a selected task's Nuke file with the last version. If the working file does not exist, it creates a new '.nk' file.

To use, the loader needs a selected task to create a working file and returns a working file as a dictionary,
which can be used later when creating an output file.

```python
browser = TaskBrowser()
comp_tasks = browser.sorted_by_due_date
selected_task = CompTask(comp_tasks[0])
load = Loader()
load.open_nuke_working_file(selected_task)
```

## Nuke Function

This module contains Nuke-related functions that can be summarized into four main categories:
setting the project, creating nodes, updating nodes, and saving/opening Nuke script.

```python
nuke_function.create_nodes(outputfile_paths)
nuke_function.update_nodes(outputfile_paths)
```

## Filetree

This module accesses to the information of file_tree from selected project.

Shows original information of the filetree, and user can change the pattern of the filetree.

If the file_tree value is None, return None.

```python
project = gazu.project.get_project_by_name("{PROJECT NAME}")
tree = FileTree(project)

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

tree.update_file_tree()
```

## Log

Create a log file and leave a record by log message.

You can find the log file that named '`molo_test.log`' on '`~/.config/Molo/`'.

### *log message for*

- information of host_url
- login access
- output file load success or fail
- Nuke file create success or fail


# How to use MOLO Widget


 MOLO Widget is a graphical user interface built on to of the MOLO API, using Pyside2.
 
 MOLO Widget contains three widgets: the Main Widget, the Login Widget, and the Host Widget.
 
 The 'Login Widget' allows users to input their ID and password, while the Host Widget provides a field for the user
 to enter the host URL. 
 
 The "Remember Me" feature saves user information in JSON format,
 which is stored locally in the ".config" directory.
 
 The 'Main widget' contains all the other main functions.
 
 
## 1) Main Widget:
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
        
        
## 2) MVC:
   2-1) Task Table Model:
        Displays data related to the output files of other tasks required by the compositor.
        
   2-2) Task Browser Model:
        Displays tasks assigned to the Compositor ana marks them as current status.
        The tooltip shows due date and priority.
        
        
## 3) MOLO Panel:
   To use MOLO Panel in Nuke:
        '~/.nuke/menu.py' :
        
        IMPORT PANEL EXAMPLE
        
        from nukescripts import panels
        from molo_main_panel import MoloWidget
        panels.registerWidgetAsPanel('MoloWidget', 'MOLO Panel', 'molo_panel.molo')
        
