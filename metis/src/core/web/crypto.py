from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad
import base64


class PasswordCrypto:
    def __init__(self, secret_key: str):
        self.key = secret_key.ljust(16)[:16]  # AES 密钥需要 16 字节

    def encrypt(self, password: str) -> str:
        cipher = AES.new(self.key.encode("utf8"), AES.MODE_CBC)
        encrypted = cipher.encrypt(
            pad(password.encode("utf8"), AES.block_size))
        return base64.b64encode(encrypted).decode("utf8")

    def decrypt(self, encrypted_password: str) -> str:
        cipher = AES.new(self.key.encode("utf8"), AES.MODE_CBC)
        decrypted = unpad(cipher.decrypt(
            base64.b64decode(encrypted_password)), AES.block_size)
        return decrypted.decode("utf8")
