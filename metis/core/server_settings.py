from typing import List
from pydantic.v1 import BaseSettings


class ServerSettings(BaseSettings):
    app_name: str = "metis"
    app_host: str = "0.0.0.0"
    app_port: int = 8001
    token: str = ""
    install_apps: str = ""
    
    class Config:
        env_file = ".env"
        
    def get_install_apps(self) -> List[str]:
        """将字符串格式的 install_apps 转换为列表"""
        if not self.install_apps:
            return []
        return [app.strip() for app in self.install_apps.split(',')]


server_settings = ServerSettings()
