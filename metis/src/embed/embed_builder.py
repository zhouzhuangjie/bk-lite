from fastembed import TextEmbedding


class EmbedBuilder:
    @staticmethod
    def get_embed(protocol: str):
        model_type = protocol.split(':')[1]
        model_name = protocol.split(':')[2]
        if model_type == 'text_embedding':
            return TextEmbedding(model_name=model_name, cache_dir="models",local_files_only=True)
        else:
            raise ValueError(f"Unsupported model type: {model_type}")
