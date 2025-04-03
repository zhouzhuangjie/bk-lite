from pydantic import BaseModel
from sanic import Blueprint, json
import tempfile
import os

rag_api_router = Blueprint("rag", url_prefix="/rag")


@rag_api_router.post("/ingest")
async def ingest(request):
    # 获取文件和知识库索引名称
    file = request.files.get('file')
    index_name = request.form.get('index_name')

    if not file or not index_name:
        return json({"status": "error", "message": "Missing required parameters: file or index_name"})

    # 检查文件类型
    allowed_types = ['docx', 'pptx', 'ppt', 'doc', 'txt', 'jpg', 'png', 'jpeg']
    file_extension = file.name.split('.')[-1].lower() if '.' in file.name else ''

    if file_extension not in allowed_types:
        return json({"status": "error", "message": f"Unsupported file type. Allowed types: {', '.join(allowed_types)}"})

    try:
        # 使用临时目录保存文件
        with tempfile.NamedTemporaryFile(delete=False, suffix=f'.{file_extension}') as temp_file:
            temp_file.write(file.body)
            temp_file.flush()
            temp_path = temp_file.name

        # 处理文件和知识库索引逻辑
        # 使用完成后删除临时文件
        os.unlink(temp_path)
        # TODO: 实现文件处理和知识库写入逻辑

        return json({"status": "success", "message": temp_path})
    except Exception as e:
        return json({"status": "error", "message": str(e)})


@rag_api_router.get("/delete_index")
async def delete_index(request):
    """
    删除知识库
    :param request:
    :return:
    """
    pass


@rag_api_router.post("/delete_doc")
async def delete_doc(request):
    """
    删除知识文档
    :param request:
    :return:
    """
    pass


@rag_api_router.post("/rag_test")
async def rag_test(request):
    """
    查询测试
    :param request:
    :return:
    """
    pass
