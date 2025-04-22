import os
from dotenv import load_dotenv
from sanic import Sanic

from src.api import api
from src.core.web.api_auth import auth
from src.core.web.config import YamlConfig
from src.core.web.crypto import PasswordCrypto
from sanic.log import logger
from langgraph.checkpoint.postgres import PostgresSaver

# 加载环境变量和配置
load_dotenv()
config = YamlConfig(path="config.yml")

# 创建全局应用实例
app = Sanic("Metis", config=config)
crypto = PasswordCrypto(os.getenv("SECRET_KEY"))
users = {
    "admin": crypto.encrypt(os.getenv("ADMIN_PASSWORD")),
}

# 配置认证


@auth.verify_password
def verify_password(username, password):
    if os.getenv('MODE') == 'DEBUG':
        return True

    if username in users:
        encrypted_password = users.get(username)
        return crypto.decrypt(encrypted_password) == crypto.decrypt(password)
    return False

# 配置启动钩子


@app.before_server_start
async def show_banner(app, loop):
    with open(f"src/asserts/banner.txt") as f:
        print(f.read())

# 注册路由
app.blueprint(api)

if __name__ == "__main__":

    logger.info("setup langgraph checkpoint")
    try:
        with PostgresSaver.from_conn_string(os.getenv('DB_URI')) as checkpointer:
            checkpointer.setup()
    except Exception as e:
        pass

    logger.info("start server")
    app.run(
        access_log=True,
        host="0.0.0.0",
        port=int(os.getenv('APP_PORT', 18083)),
        workers=1
    )
