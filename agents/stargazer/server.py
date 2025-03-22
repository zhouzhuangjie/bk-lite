from sanic import Sanic
from sanic.response import text
from api import api
from core.config import YamlConfig

yml_config = YamlConfig(path="./config.yml")
app = Sanic("Stargazer", config=yml_config)
app.blueprint(api)


@app.before_server_start
async def show_banner(app, loop):
    with open(f"./asserts/banner.txt") as f:
        print(f.read())


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8083, workers=1)
