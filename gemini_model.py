import os
from pathlib import Path
import google.generativeai as genai
from dotenv import load_dotenv

class GeminiModel:
    def __init__(self):
        load_dotenv()
        genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

        # Model Configuration
        self.MODEL_CONFIG = {
            "temperature": 0.2,
            "top_p": 1,
            "top_k": 32,
            "max_output_tokens": 4096,
        }

        ## Safety Settings of Model
        self.safety_settings = [
            {"category": "HARM_CATEGORY_HARASSMENT", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
            {"category": "HARM_CATEGORY_HATE_SPEECH", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
            {"category": "HARM_CATEGORY_SEXUALLY_EXPLICIT", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
            {"category": "HARM_CATEGORY_DANGEROUS_CONTENT", "threshold": "BLOCK_MEDIUM_AND_ABOVE"}
        ]

        self.model = genai.GenerativeModel(model_name="gemini-pro-vision",
                                           generation_config=self.MODEL_CONFIG,
                                           safety_settings=self.safety_settings)

    def image_format(self, image_path):
        img = Path(image_path)

        if not img.exists():
            raise FileNotFoundError(f"Could not find image: {img}")

        image_parts = [
            {
                "mime_type": "image/png",  # Mime type are PNG - image/png. JPEG - image/jpeg. WEBP - image/webp
                "data": img.read_bytes()
            }
        ]
        return image_parts

    def generate(self, image_path, system_prompt, user_prompt):
        image_info = self.image_format(image_path)
        input_prompt = [system_prompt, image_info[0], user_prompt]
        response = self.model.generate_content(input_prompt)
        return response.text