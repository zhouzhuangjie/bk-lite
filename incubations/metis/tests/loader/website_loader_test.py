import os
from dotenv import load_dotenv

from src.loader.website_loader import WebSiteLoader
load_dotenv()


def test_website_loader():
    loader = WebSiteLoader(url=os.getenv('TEST_WEBSITE_LOADER_BASE_URL'),
                           max_depth=1)

    print(loader.load())
