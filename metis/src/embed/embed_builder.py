from fastembed import TextEmbedding

@staticmethod
class EmbedBuilder:
    embedding = TextEmbedding(model_name="BAAI/bge-small-zh-v1.5", cache_dir="models")