import logging
import subprocess
from abc import ABC
from typing import Union, List, Tuple

from IOSSystem import IOSSystem


class LinuxIOSSystem(IOSSystem):

    def execute(self, command: Union[str, List[str]], cwd: str, use_shell: bool = True, capture_stdout: bool = True) -> \
    Tuple[int, str, str]:
        result = subprocess.run(command, cwd=cwd, shell=use_shell, capture_output=capture_stdout)
        if result.returncode != 0:
            raise ValueError(f"cwd={cwd} command={command} exit={result.returncode}")

        if capture_stdout:
            stdout = self._convert_stdout(result.stdout)
            stderr = self._convert_stdout(result.stderr)
        else:
            stdout = ""
            stderr = ""
        return result.returncode, stdout, stderr

    def execute_admin(self, command: Union[str, List[str]], cwd: str, use_shell: bool = True,
                      capture_stdout: bool = True):
        if isinstance(command, str):
            return self.execute(command=f"sudo {command}", cwd=cwd, use_shell=use_shell, capture_stdout=capture_stdout)
        elif isinstance(command, list):
            tmp = ["sudo"]
            tmp.extend(command)
            return self.execute(command=tmp, cwd=cwd, use_shell=use_shell, capture_stdout=capture_stdout)
        else:
            raise TypeError(f"invalid command type {type(command)}")
