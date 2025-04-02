import base64
import json
from io import BytesIO
from typing import List

import torch
from PIL import Image
from langchain_core.documents import Document
from langchain_core.runnables import RunnableLambda
from langserve import add_routes
from loguru import logger
from modelscope import AutoProcessor, Qwen2VLForConditionalGeneration

from core.user_types.ocr_request import OcrRequest


class OlmOcrRunnable():
    def __init__(self):
        self.model = Qwen2VLForConditionalGeneration.from_pretrained("allenai/olmOCR-7B-0225-preview", torch_dtype=torch.bfloat16).eval()
        self.processor = AutoProcessor.from_pretrained("allenai/olmOCR-7B-0225-preview")
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self.model.to(self.device)

    def predict(self, request: OcrRequest) -> List[Document]:
        prompt = """
            Below is the image of one page of a document, as well as some raw textual content that was previously extracted for it. 
            Just return the plain text representation of this document as if you were reading it naturally.
            Do not hallucinate.
        """
        messages = [
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": prompt},
                    {"type": "image_url", "image_url": {"url": f"{request.file}"}},
                ],
            }
        ]
        text = self.processor.apply_chat_template(messages, tokenize=False, add_generation_prompt=True)
        main_image = Image.open(BytesIO(base64.b64decode(request.file)))
        inputs = self.processor(
            text=[text],
            images=[main_image],
            padding=True,
            return_tensors="pt",
        )
        inputs = {key: value.to(self.device) for (key, value) in inputs.items()}
        output = self.model.generate(
            **inputs,
            temperature=0.8,
            max_new_tokens=8000,
            num_return_sequences=1,
        )
        prompt_length = inputs["input_ids"].shape[1]
        new_tokens = output[:, prompt_length:]
        text_output = self.processor.tokenizer.batch_decode(
            new_tokens, skip_special_tokens=True
        )
        logger.info(text_output)
        result = []
        for obj in text_output:
            result.append(json.loads(obj)['natural_text'])
        return result

    def register(self, app):
        add_routes(app,
                   RunnableLambda(self.predict).with_types(input_type=OcrRequest, output_type=List[Document]),
                   path='/olmocr')
