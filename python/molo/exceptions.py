#! /usr/bin/env molo
"""
exceptions - Exception subclasses relevant to mola operations.
"""


class MoloException(Exception):
    """
    Molo에 대한 일반적인 예외 상황
    """
    pass


class AuthFileIOError(MoloException):
    """
    로그인과 관련한 파일 생성 및 입출력에 실패한 경우
    """
    pass


class UnconnectedHostError(MoloException):
    """
    host에 연결되어 있지 않은 상태에서 login을 시도한 경우
    """
    pass


class InvalidAuthError(MoloException):
    """
    유효하지 않은 host, id, pw 값으로 연결을 시도한 경우
    """
    pass


class DictTypeError(MoloException):
    """
    입력으로 들어온 dict의 type이 부적절한 경우
    """
    pass


class WorkingFileExistsError(MoloException):
    """
    생성하고자 하는 working file 경로에 파일이 이미 존재하는 경우
    """
    pass


class InvalidNukePathError(MoloException):
    """
    설치된 Nuke 경로가 없는 경우
    """
    pass

class TaskTypeFileIOError(MoloException):
    """
    TaskType 관련한 JSON파일 생성 및 입출력에 실패한 경우
    """
    pass
