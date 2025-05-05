class EmbedBuilder:
    _embed_instances = {}

    @classmethod
    def get_embed_instance(cls, protocol: str):
        from langchain_huggingface import HuggingFaceEmbeddings

        model_type = protocol.split(':')[1]
        model_name = protocol.split(':')[2]
        if model_type == 'huggingface_embedding' and cls._embed_instances.get(protocol, None) is None:
            cls._embed_instances[protocol] = HuggingFaceEmbeddings(
                model_name=model_name,
                model_kwargs={'device': 'cpu'},
                encode_kwargs={'normalize_embeddings': False},
                cache_folder="./models"
            )
        return cls._embed_instances[protocol]

    @staticmethod
    def get_embed(protocol: str):
        return EmbedBuilder.get_embed_instance(protocol)
