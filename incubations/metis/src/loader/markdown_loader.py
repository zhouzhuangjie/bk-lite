class MarkdownLoader:
    def __init__(self, path: str):
        self.path = path

    def load(self) -> str:
        with open(self.path, 'r', encoding='utf-8') as file:
            content = file.read()
        return content
