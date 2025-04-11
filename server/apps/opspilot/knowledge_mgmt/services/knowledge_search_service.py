from typing import Any, Dict, List

from django.conf import settings
from langserve import RemoteRunnable

from apps.opspilot.knowledge_mgmt.models import KnowledgeBase
from apps.opspilot.models import EmbedProvider, RerankProvider


class KnowledgeSearchService:
    @staticmethod
    def _build_search_params(
        knowledge_base_folder: KnowledgeBase,
        query: str,
        embed_model_address: str,
        rerank_model_address: str,
        kwargs: Dict[str, Any],
    ) -> Dict[str, Any]:
        """构建搜索参数

        Args:
            knowledge_base_folder: 知识库文件夹对象
            query: 搜索查询
            embed_model_address: 嵌入模型地址
            rerank_model_address: 重排序模型地址
            kwargs: 搜索配置参数

        Returns:
            Dict[str, Any]: 构建好的搜索参数字典
        """
        params = {
            "elasticsearch_url": settings.ELASTICSEARCH_URL,
            "elasticsearch_password": settings.ELASTICSEARCH_PASSWORD,
            "embed_model_address": embed_model_address,
            "index_name": knowledge_base_folder.knowledge_index_name(),
            "search_query": query,
            "metadata_filter": {"enabled": True},
            "rag_k": kwargs["rag_k"],
            "rag_num_candidates": kwargs["rag_num_candidates"],
            "enable_rerank": kwargs["enable_rerank"],
            "rerank_model_address": rerank_model_address,
            "rerank_top_k": kwargs["rerank_top_k"],
            "size": knowledge_base_folder.result_count,
            "enable_text_search": kwargs["enable_text_search"],
            "enable_vector_search": kwargs["enable_vector_search"],
            "text_search_mode": kwargs["text_search_mode"],
        }

        if kwargs["enable_text_search"]:
            params["text_search_weight"] = kwargs["text_search_weight"]
        if kwargs["enable_vector_search"]:
            params["vector_search_weight"] = kwargs["vector_search_weight"]

        return params

    @classmethod
    def search(
        cls, knowledge_base_folder: KnowledgeBase, query: str, kwargs: Dict[str, Any], score_threshold: float = 0
    ) -> List[Dict[str, Any]]:
        """执行知识库搜索

        Args:
            knowledge_base_folder: 知识库文件夹对象
            query: 搜索查询语句
            kwargs: 搜索配置参数
            score_threshold: 分数阈值，低于此分数的结果将被过滤

        Returns:
            List[Dict[str, Any]]: 搜索结果列表
        """
        docs = []
        remote_indexer = RemoteRunnable(settings.RAG_SERVER_URL)

        # 获取嵌入模型地址
        embed_model_address = EmbedProvider.objects.get(id=kwargs["embed_model"]).embed_config["base_url"]

        # 获取重排序模型地址
        rerank_model_address = ""
        if kwargs["enable_rerank"]:
            rerank_model_address = RerankProvider.objects.get(id=kwargs["rerank_model"]).rerank_config["base_url"]

        # 构建搜索参数
        params = cls._build_search_params(
            knowledge_base_folder, query, embed_model_address, rerank_model_address, kwargs
        )

        # 执行搜索
        result = remote_indexer.invoke(params)

        # 处理搜索结果
        for doc in result:
            score = doc.metadata["_score"] * 10
            if score <= score_threshold:
                continue

            doc_info = {
                "content": doc.page_content,
                "score": score,
                "knowledge_id": doc.metadata["_source"]["metadata"]["knowledge_id"],
                "knowledge_title": doc.metadata["_source"]["metadata"]["knowledge_title"],
            }

            if kwargs["enable_rerank"]:
                doc_info["rerank_score"] = doc.metadata["relevance_score"]

            docs.append(doc_info)

        # 按分数降序排序
        docs.sort(key=lambda x: x["score"], reverse=True)
        return docs
