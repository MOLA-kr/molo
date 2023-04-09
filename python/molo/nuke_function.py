import os
import nuke
import fileseq
from PySide2 import QtCore


def project_setting(comptask):
    """
    해당 comptask의 frame_in, frame_out, resolution, fps를 받아서
    nuke script의 project settings을 변경한다.
    resolution의 경우는 format을 만들어 세팅한다.

    """
    frame_in = int(comptask.frame_in)
    frame_out = int(comptask.frame_out)
    resolution = comptask.resolution
    width, height = resolution.split('x')
    format_name = f'molo_{width}*{height}'
    fps = int(comptask.fps)

    nuke.addFormat(f'{width} {height} {format_name}')

    nuke.root()['first_frame'].setValue(frame_in)
    nuke.root()['last_frame'].setValue(frame_out)
    nuke.root()['format'].setValue(format_name)
    nuke.root()['fps'].setValue(fps)


def nodes_data():
    """
    nuke에 존재하는 node들에서 molo_id와 task_type 값 추출

    Returns:
        source_dic (dict): 존재하는 모든 node들의 task_type을 key, molo_id를 value로 하는 dict
    """
    nodes = nuke.allNodes()
    source_dic = {}

    for node in nodes:
        if not (node.knob('task_type') and node.knob('molo_id')):
            continue
        node_type = node["task_type"].value()
        node_id = node["molo_id"].value()
        source_dic[node_type] = node_id

    return source_dic


def create_node(object_type, molo_id, task_path, xpos, ypos):
    """

    Args:
        object_type:
        molo_id:
        task_path:
        xpos:
        ypos:

    Returns: bool

    """
    """
    선택한 output file에 해당하는 Camera노드 또는 Read노드를 생성한다.
    """
    if task_path.endswith((".fbx", ".abc", ".usd")):
        if not os.path.exists(task_path):
            print("해당하는 파일이 경로에 없습니다.")
            return False
        cam = nuke.nodes.Camera3(file=task_path, xpos=xpos + 200, ypos=ypos + 150)
        cam.addKnob(nuke.Text_Knob('molo_id', 'DB_id'))
        cam.addKnob(nuke.Text_Knob('task_type', 'Task_Type'))
        cam['molo_id'].setValue(molo_id)
        cam['task_type'].setValue(object_type)
        cam.setSelected(True)

    elif task_path.endswith(('.exr', '.jpg', '.png', '.dpx', '.mov', '.mp4')):
        try:
            seq = fileseq.findSequenceOnDisk(task_path)
        except fileseq.FileSeqException:
            print("해당하는 파일이 경로에 없습니다.")
            return False
        first = seq.start()
        last = seq.end()
        node = nuke.nodes.Read(file=task_path, first=first, last=last, xpos=xpos + 200, ypos=ypos + 150)
        node.addKnob(nuke.Text_Knob('molo_id', 'DB_id'))
        node.addKnob(nuke.Text_Knob('task_type', 'Task_Type'))
        node['molo_id'].setValue(molo_id)
        node['task_type'].setValue(object_type)
        node.setSelected(True)
    nuke.nodes.BackdropNode(xpos=xpos, ypos=ypos, bdwidth=500, bdheight=400, label=object_type,
                            note_font_size=35)


def create_nodes(info_dict, log_func=None):
    """
    누크 노드 템플릿 생성. (constant 노드, merge 노드, backdrop 노드 포함)
    각 output file 별로 Camera노드와 Read노드를 생성한다.
    기존 파일의 노드 그래프 상 모든 노드의 위치를 확인하여 자동으로 중복되지 않는 위치에 생성한다.
    """
    # c1 = nuke.nodes.Constant(xpos=0, ypos=0)
    # m1 = nuke.nodes.Merge(inputs=[c1, None])
    # m2 = nuke.nodes.Merge(inputs=[m1, None])
    # m3 = nuke.nodes.Merge(inputs=[m2, None])
    # R1 = nuke.nodes.Reformat()
    if not info_dict:
        return

    xpos, ypos = get_nodes_bound()
    for object_type, path_list in info_dict.items():
        for molo_id, file_path in path_list.items():
            res = create_node(object_type, molo_id, file_path, xpos, ypos)
            if log_func and res:
                # 나중에 수정 필요
                log_func(file_path + ' create!')
            xpos += 600


def update_nodes(info_dict, log_func=None):
    """
    누크 내 파일이 최신 버젼이 아닌 경우, 경로와 ID를 최신파일로 바꿔준다.

    Args:
        info_dict:
        log_func:

    Returns:

    """
    if not info_dict:
        return

    nodes = nuke.allNodes()
    # 누크 내에 있는 모든 노드들의 task_type_name을 가져옴.
    for node in nodes:
        node.setSelected(False)
        if not (node.knob('task_type') and node.knob('molo_id')):
            continue
        node_type = node["task_type"].value()
        if node_type in info_dict.keys():
            molo_id = next(iter(info_dict[node_type].keys()))
            file_path = next(iter(info_dict[node_type].values()))
            if not os.path.exists(file_path):
                print("해당하는 파일이 경로에 없습니다.")
                continue
            if file_path.endswith(('.exr', '.jpg', '.png', '.dpx', '.mov', '.mp4')):
                try:
                    seq = fileseq.findSequenceOnDisk(file_path)
                except fileseq.FileSeqException:
                    print("해당하는 파일이 경로에 없습니다.")
                    continue
                node["molo_id"].setValue(molo_id)
                node["file"].setValue(file_path)
                first = seq.start()
                last = seq.end()
                node["first"].setValue(first)
                node["last"].setValue(last)
            node.setSelected(True)
            if log_func:
                # 나중에 수정 필요
                log_func(file_path + ' update!')


def get_node_rect(node):
    """
    노드 그래프 상 배치되어 있는 노드의 범위를 파악하여 직사각형 형태로 좌표와 그 크기를 반환
    Args:
        node: Nuke node

    Returns: 노드 그래프 상 노드들의 범위의 좌표값과 사이즈 반환
    """

    return QtCore.QRectF(node.xpos(), node.ypos(), node.screenWidth(), node.screenHeight())


def get_nodes_bound():
    """
    노드 그래프 상에 있는 모든 노드의 범위(사각형 형태)를 계산, 각 범위를 합산하여 출력한다.

    Returns: 노드 전체 범위의 (x,y) 좌표

    """
    # Get a list of all the rectangles
    all_rects = [get_node_rect(n) for n in nuke.allNodes()]

    if not all_rects:
        return 0, 0

    # Unite all the rectangles
    united_rect = None
    for rect in all_rects:
        united_rect = united_rect.united(rect) if united_rect else rect

    # Expand the bounds to add a little border.
    united_rect.adjust(0, -600, 0, 0)

    return united_rect.left(), united_rect.top()


def save_script(working_file_path):
    """
    self.working_file_path 경로로 nuke script를 저장한다.

    Args:
        working_file_path(str): self.working_file_path 경로
    """
    nuke.scriptSaveAs(working_file_path)


def clear_current_nuke_file():
    """
    현재 열려있는 nuke script 초기화
    modified이면 저장 여부 확인 후 진행
    """
    modified = nuke.root().modified()
    if modified:
        answer = nuke.ask("Save changes before open script?")
        if answer:
            nuke.scriptSave()
    nuke.scriptClear()


def open_current_nuke_file(working_file_path):
    """
    해당 self.working_file_path경로를 가진 nuke script를 오픈한다.

    Args:
        working_file_path(str): 해당 self.working_file_path경로
    """
    nuke.scriptOpen(working_file_path)


def nuke_file_name():
    """
    현재 열려있는 nuke script의 경로와 이름을 반환한다.

        Returns: 현재 열려있는 nuke script의 경로와 이름
    """
    path = nuke.value("root.name")
    return path


def focus_selected_node():
    """
    user가 발견하기 편하게 생성 또는 업데이트로 변화가 생긴 노드를 하이라이트 및 zoom한다.
    """
    nuke.zoomToFitSelected()

def deselect_all_nodes():
    """
    User가 Nuke에서 작업 중 선택한 노드들의 선택을 해제한다.
    """
    for n in nuke.allNodes():
        n.setSelected(False)
