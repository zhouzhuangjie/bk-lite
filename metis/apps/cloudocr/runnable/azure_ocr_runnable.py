import base64
import time
from io import BytesIO
from typing import List

from azure.cognitiveservices.vision.computervision import ComputerVisionClient
from azure.cognitiveservices.vision.computervision.models import OperationStatusCodes
from langchain_core.documents import Document
from langchain_core.runnables import RunnableLambda
from langserve import add_routes
from msrest.authentication import CognitiveServicesCredentials

from apps.cloudocr.user_types.azure_ocr_request import AzureOcrRequest


class AzureOcrRunnable:

    def execute(self, request: AzureOcrRequest) -> List[Document]:
        computervision_client = ComputerVisionClient(request.azure_ocr_endpoint,
                                                     CognitiveServicesCredentials(request.azure_ocr_key))
        base_image = base64.b64decode(request.file)
        read_response = computervision_client.read_in_stream(BytesIO(base_image), raw=True)
        read_operation_location = read_response.headers["Operation-Location"]
        operation_id = read_operation_location.split("/")[-1]
        while True:
            read_result = computervision_client.get_read_result(operation_id)
            if read_result.status not in ['notStarted', 'running']:
                break
            time.sleep(1)

        content = ''
        if read_result.status == OperationStatusCodes.succeeded:
            for text_result in read_result.analyze_result.read_results:
                for line in text_result.lines:
                    content += line.text + ' '

        docs = [Document(page_content=content)]
        return docs

    def register(self, app):
        add_routes(app,
                   RunnableLambda(self.execute).with_types(input_type=AzureOcrRequest, output_type=List[Document]),
                   path='/azure_ocr')

    def instance(self):
        return RunnableLambda(self.execute).with_types(input_type=AzureOcrRequest, output_type=List[Document])
