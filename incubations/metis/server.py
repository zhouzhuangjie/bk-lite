import os

from dotenv import load_dotenv
from sanic import Sanic
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad
import base64

from src.api import api
from src.core.web.api_auth import auth
from src.core.web.config import YamlConfig

load_dotenv()
yml_config = YamlConfig(path="config.yml")

app = Sanic("Metis", config=yml_config)


def encrypt_password(key, password):
    cipher = AES.new(key.encode("utf8"), AES.MODE_CBC)  # 去掉 iv 参数
    encrypted = cipher.encrypt(pad(password.encode("utf8"), AES.block_size))
    return base64.b64encode(encrypted).decode("utf8")


def decrypt_password(key, encrypted_password):
    cipher = AES.new(key.encode("utf8"), AES.MODE_CBC)  # 去掉 iv 参数
    decrypted = unpad(cipher.decrypt(
        base64.b64decode(encrypted_password)), AES.block_size)
    return decrypted.decode("utf8")


app_salt = os.getenv("SECRET_KEY").ljust(16)[:16]  # AES 密钥需要 16 字节
users = {
    "admin": encrypt_password(app_salt, os.getenv("ADMIN_PASSWORD")),
}


@auth.verify_password
def verify_password(username, password):
    if os.getenv('MODE') == 'DEBUG':
        return True

    if username in users:
        encrypted_password = users.get(username)
        return decrypt_password(app_salt, encrypted_password) == password
    return False


@app.before_server_start
async def show_banner(app, loop):
    with open(f"src/asserts/banner.txt") as f:
        print(f.read())

app.blueprint(api)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=os.getenv('APP_PORT', 18083), workers=1)
