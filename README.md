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
