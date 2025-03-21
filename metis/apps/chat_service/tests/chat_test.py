import os
import time
import unittest
import asyncio
from langserve import RemoteRunnable
from dotenv import load_dotenv

load_dotenv()


class TestChatService(unittest.TestCase):
    def setUp(self):
        self.client = RemoteRunnable('http://127.0.0.1:8005/openai/stream')
        self.test_input = {
            "openai_api_base": os.getenv('OPENAI_BASE_URL'),
            "openai_api_key": os.getenv('OPENAI_API_KEY'),
            "model": "gpt-4o",
            "user_message": "你好",
            "chat_history": [],
            "image_data": [
            ]
        }

    async def async_test_chat_stream(self):
        chunks = []
        async for chunk in self.client.astream(self.test_input):
            time.sleep(0.1)
            print(chunk)
            # content = chunk.get('content', '')

            # print(content, end='', flush=True)  # Print content in real-time
            # chunks.append(chunk)

    def test_chat_stream(self):
        asyncio.run(self.async_test_chat_stream())


if __name__ == '__main__':
    unittest.main()
