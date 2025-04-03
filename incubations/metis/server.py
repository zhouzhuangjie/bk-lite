import os

from dotenv import load_dotenv
from sanic import Sanic

from src.api import api
from src.core.web.config import YamlConfig

load_dotenv()
yml_config = YamlConfig(path="config.yml")
app = Sanic("Metis", config=yml_config)

app.blueprint(api)


@app.before_server_start
async def show_banner(app, loop):
    with open(f"src/asserts/banner.txt") as f:
        print(f.read())


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=os.getenv('APP_PORT', 18083), workers=1)
