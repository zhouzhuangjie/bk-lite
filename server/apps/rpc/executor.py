from server.apps.rpc.base import RpcClient


class Executor(object):
    def __init__(self, instance_id):
        """
        命令执行客户端
        :param instance_id: 执行器实例ID
        """
        self.instance_id = instance_id
        self.local_client = RpcClient('local.execute')
        self.ssh_client = RpcClient('ssh.execute')

    def execute_local(self, command, working_directory=None, timeout=60):
        """
        执行本地命令
        :param command: 要执行的命令
        :param working_directory: 工作目录
        :param timeout: 执行超时时间(秒)
        :return: 命令执行结果
        """
        request_data = {
            "command": command,
            "working_directory": working_directory,
            "timeout": timeout
        }
        return_data = self.local_client.run(self.instance_id, **request_data)
        return return_data

    def execute_ssh(self, command, host, username, password=None, key_file=None, timeout=60):
        """
        通过SSH执行远程命令
        :param command: 要执行的命令
        :param host: 远程主机地址
        :param username: SSH用户名
        :param password: SSH密码(可选)
        :param key_file: SSH密钥文件路径(可选)
        :param timeout: 执行超时时间(秒)
        :return: 命令执行结果
        """
        request_data = {
            "command": command,
            "host": host,
            "username": username,
            "timeout": timeout
        }

        # 添加可选参数
        if password:
            request_data["password"] = password
        if key_file:
            request_data["key_file"] = key_file

        return_data = self.ssh_client.run(self.instance_id, **request_data)
        return return_data
