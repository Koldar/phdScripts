import abc
from typing import Union, List, Tuple


class IOSSystem(abc.ABC):

    @abc.abstractmethod
    def execute(self, command: Union[str, List[str]], cwd: str, use_shell: bool = True,
                      capture_stdout: bool = True) -> Tuple[int, str, str]:
        pass

    @abc.abstractmethod
    def execute_admin(self, command: Union[str, List[str]], cwd: str, use_shell: bool = True, capture_stdout: bool = True) -> Tuple[int, str, str]:
        pass

    def _convert_stdout(self, stdout) -> str:
        if isinstance(stdout, bytes):
            stdout = stdout.decode("utf-8")
        elif isinstance(stdout, list):
            tmp = []
            for x in stdout:
                if isinstance(x, bytes):
                    tmp.append(x.decode("utf-8"))
                elif isinstance(x, str):
                    tmp.append(x)
                else:
                    raise TypeError(f"invalid stdout output type {type(x)}!")
            stdout = ''.join(tmp)
        elif isinstance(stdout, str):
            stdout = str(stdout)
        else:
            raise TypeError(f"invalid stdout output type {type(stdout)}!")

        return stdout
