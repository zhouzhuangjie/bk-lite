# -- coding: utf-8 --
# @File: nast_request.py
# @Time: 2025/4/25 11:14
# @Author: windyzhao

import asyncio
import nats
import json


async def main():
    nc = await nats.connect("")
    response = await nc.request("system_mgmt.get_client", b'{"node":"node"}', timeout=0.5)
    print(f"Received a message: {json.loads(response.data.decode())}")

    await nc.drain()


if __name__ == '__main__':
    asyncio.run(main())
