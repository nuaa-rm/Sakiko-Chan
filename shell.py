import os
import fcntl
import subprocess
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
            stderr=subprocess.PIPE,  # 捕获标准错误
            text=True,
            shell=False
        )

        # 设置 stdout 和 stderr 为非阻塞模式
        for pipe in [self.process.stdout, self.process.stderr]:
            fd = pipe.fileno()
            flags = fcntl.fcntl(fd, fcntl.F_GETFL)
            fcntl.fcntl(fd, fcntl.F_SETFL, flags | os.O_NONBLOCK)

    def run_command(self, command: str) -> str:
        """
        运行命令并返回结果（包括错误信息）。
        """
        if not self.process.stdin or not self.process.stdout:
            return "Shell process is not running."

        self.process.stdin.write(command + "\n")
        self.process.stdin.flush()

        # 等待并非阻塞地读取输出
        output = []
        error = []
        while True:
            ready, _, _ = select([self.process.stdout, self.process.stderr], [], [], 1.0)
            if ready:
                for pipe in ready:
                    line = pipe.read()
                    if line:
                        if pipe == self.process.stdout:
                            output.append(line)
                        elif pipe == self.process.stderr:
                            error.append(line)
                    else:
                        break
            else:
                break

        result = "".join(output).strip()
        error_msg = "".join(error).strip()

        # 合并输出和错误信息，或者根据需求单独返回
        if error_msg:
            return f"Error: {error_msg}"
        return result

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
        print(shell.run_command("cd src"))  # src 不存在时返回错误信息
        print(shell.run_command("ls"))     # 列出当前目录文件
        print(shell.run_command("pwd"))    # 打印当前工作目录
    finally:
        shell.close()
