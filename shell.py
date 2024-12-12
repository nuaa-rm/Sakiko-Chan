import os
import fcntl
import subprocess
import time
from select import select

class PersistentShell:
    def __init__(self):
        """
        初始化一个持久化 Shell 子进程。
        """
        self.process = subprocess.Popen(
            "/bin/bash",  # 启动一个 Bash 终端
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            shell=False
        )

        # 设置 stdout 为非阻塞
        fd = self.process.stdout.fileno()
        flags = fcntl.fcntl(fd, fcntl.F_GETFL)
        fcntl.fcntl(fd, fcntl.F_SETFL, flags | os.O_NONBLOCK)

    def run_command(self, command: str) -> str:
        """
        运行命令并返回结果。
        """
        if not self.process.stdin or not self.process.stdout:
            return "Shell process is not running."

        self.process.stdin.write(command + "\n")
        self.process.stdin.flush()

        # 等待并非阻塞地读取输出
        output = []
        while True:
            # 使用 select 等待输出变得可读
            ready, _, _ = select([self.process.stdout], [], [], 1.0)
            if ready:
                line = self.process.stdout.read()
                if line:
                    output.append(line)
                else:
                    break
            else:
                break
        return "".join(output)

    def close(self):
        """
        关闭子进程。
        """
        if self.process.stdin:
            self.process.stdin.close()
        if self.process.stdout:
            self.process.stdout.close()
        if self.process.stderr:
            self.process.stderr.close()
        self.process.terminate()

# 使用示例
if __name__ == "__main__":
    shell = PersistentShell()
    try:
        print(shell.run_command("cd src"))
        print(shell.run_command("ls"))
        print(shell.run_command("pwd"))
    finally:
        shell.close()
