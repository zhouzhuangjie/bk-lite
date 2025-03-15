import importlib
from typing import Annotated

import uvicorn
from dotenv import load_dotenv
from fastapi import Depends, Header, HTTPException
from fastapi import FastAPI
from loguru import logger
from starlette.middleware.cors import CORSMiddleware

from core.server_settings import server_settings


class Bootstrap:
    def __init__(self):
        load_dotenv()

        if server_settings.token == "":
            self.app = FastAPI(title=server_settings.app_name)
        else:
            self.app = FastAPI(title=server_settings.app_name, dependencies=[Depends(self.verify_token)])

    async def verify_token(self, x_token: Annotated[str, Header()]) -> None:
        if x_token != server_settings.token:
            raise HTTPException(status_code=400, detail="Token is invalid")

    def setup_middlewares(self):
        self.app.add_middleware(
            CORSMiddleware,
            allow_origins=["*"],
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
            expose_headers=["*"],
        )

    def setup_router(self):
        for app_path in server_settings.get_install_apps():
            try:
                module = importlib.import_module(f'apps.{app_path}.routes')
                if hasattr(module, 'register_routes'):
                    module.register_routes(self.app)
            except ModuleNotFoundError:
                logger.warning(f"app not found: {app_path}")

    def start(self):
        self.setup_middlewares()
        self.setup_router()
        uvicorn.run(self.app, host=server_settings.app_host, port=server_settings.app_port)
