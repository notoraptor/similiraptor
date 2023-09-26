import sys
import os

FileSystem = os


class UnsupportedSystemError(SystemError):
    pass


class System:
    @staticmethod
    def is_windows():
        return sys.platform == "win32"

    @staticmethod
    def is_linux():
        return sys.platform == "linux"

    @staticmethod
    def is_mac():
        return sys.platform == "darwin"

    @staticmethod
    def platform():
        return sys.platform

    @staticmethod
    def get_lib_basename(name, prefix="lib"):
        if System.is_windows():
            return f"{name}.dll"
        elif System.is_linux():
            return f"{prefix}{name}.so"
        else:
            raise UnsupportedSystemError(System.platform())
