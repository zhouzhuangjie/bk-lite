from typing import TypedDict

from langchain_core.messages import SystemMessage, HumanMessage, AIMessage
from langchain_core.runnables import RunnableConfig
from langchain_openai import ChatOpenAI

from src.core.entity.basic_llm_request import BasicLLMReuqest
from src.rag.native_rag.elasticsearch_rag import ElasticSearchRag


class BasicNode:

    def get_llm_client(self, request: BasicLLMReuqest) -> ChatOpenAI:
        llm = ChatOpenAI(model=request.model, base_url=request.openai_api_base,
                         api_key=request.openai_api_key, temperature=request.temperature)
        return llm

    def prompt_message_node(self, state: TypedDict, config: RunnableConfig) -> TypedDict:
        if config["configurable"]["graph_request"].system_message_prompt:
            state["messages"].append(
                SystemMessage(content=config["configurable"]["graph_request"].system_message_prompt)
            )
        return state

    def add_chat_history_node(self, state: TypedDict, config: RunnableConfig) -> TypedDict:
        if config["configurable"]['graph_request'].chat_history:
            for chat in config["configurable"]['graph_request'].chat_history:
                if chat.event == 'user':
                    if chat.image_data:
                        state['messages'].append(HumanMessage(content=[
                            {"type": "text", "text": "describe the weather in this image"},
                            {"type": "image_url", "image_url": {"url": chat.image_data}},
                        ]))
                    else:
                        state['messages'].append(HumanMessage(content=chat.message))
                elif chat.event == 'assistant':
                    state['messages'].append(AIMessage(content=chat.message))
        return state

    def naive_rag_node(self, state: TypedDict, config: RunnableConfig) -> TypedDict:
        if config["configurable"]['graph_request'].enable_naive_rag is False:
            return state

        naive_rag_request = config["configurable"]["graph_request"].naive_rag_request
        if len(naive_rag_request) == 0:
            return state

        for rag_search_request in naive_rag_request:
            elasticsearch_rag = ElasticSearchRag()
            rag_result = elasticsearch_rag.search(rag_search_request)
            rag_message = f'''
                以下是参考资料,每份参考资料都由标题和内容组成,以XML格式提供:
                
                示例:
                    <knowledge>
                        <ref_id>1</ref_id>
                        <title>知识标题</title>
                        <content>知识内容</content>
                    </knowledge>
                
                字段说明:
                    ref_id: 是第几份参考资料，从1开始
                    title: 参考资料的标题
                    content: 参考资料的内容
                    
                参考资料:
            '''
            for index, r in enumerate(rag_result):
                rag_message += f"""
                    <knowledge>
                        <ref_id>{index + 1}</ref_id>
                        <title>{r.metadata['_source']['metadata']['knowledge_title']}</title>
                        <knowledge_id>{r.metadata['_source']['metadata']['knowledge_id']}</knowledge_id>
                        <chunk_number>{r.metadata['_source']['metadata']['chunk_number']}</chunk_number>
                        <segment_number>{r.metadata['_source']['metadata']['segment_number']}</segment_number>
                        <segment_id>{r.metadata['_source']['metadata']['segment_id']}</segment_id>
                        <content>{r.page_content}</content>
                    </knowledge>
                """

                if rag_search_request.enable_rag_source is True:
                    rag_message += f"""
                    在回复中,请使用XML格式返回参考资料,并且在每个参考资料的前面加上序号,例如:[1]、[2]、[3]等，指观点引用自哪份材料。
                    在回复我的信息最后进行补充：
                        
                        这里是回复的内容
                        ------------------
                        参考资料:
                            <result>
                                <rag>
                                    <ref_id>1</ref_id>
                                    <knowledge_id>1</knowledge_id>
                                    <segment_number>1</segment_number>
                                    <chunk_number>1</chunk_number>
                                    <segment_id>1</segment_id>
                                    <title>知识标题</title>
                                </rag>
                                <rag>
                                    <ref_id>12</ref_id>
                                    <knowledge_id>0</knowledge_id>
                                    <segment_number>13</segment_number>
                                    <chunk_number>1</chunk_number>
                                    <segment_id>5</segment_id>
                                    <title>知识标题</title>
                                </rag>                            
                            </result>
                    
                """
            state["messages"].append(HumanMessage(content=rag_message))
        return state

    def user_message_node(self, state: TypedDict, config: RunnableConfig) -> TypedDict:
        state["messages"].append(HumanMessage(content=config["configurable"]["graph_request"].user_message))
        return state
