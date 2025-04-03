import base64


class ImageLoader:
    def __init__(self, path):
        self.path = path

    def load(self):
        docs = []
        with open(self.path, "rb") as file:
            for doc in docs:
                doc.metadata["format"] = "image"
        return docs
