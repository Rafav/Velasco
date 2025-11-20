import os
import dashscope
# The following is the URL for the Singapore region. If you use a model in the Beijing region, replace the URL with: https://dashscope.aliyuncs.com/api/v1
dashscope.base_http_api_url = 'https://dashscope-intl.aliyuncs.com/api/v1'

# Replace xxx/test.jpg with the absolute path of your local image.
local_path = "xxx/test.jpg"
image_path = f"file:///home/rafa/Descargas/Velasco/a_jpg_afinado/pagina_0002.jpg"
messages = [
    {
        "role": "user",
        "content": [
            {
                "image": image_path,
                # The minimum pixel threshold for the input image. If the image is smaller, it is scaled up proportionally until its total pixels exceed min_pixels.
                "min_pixels": 65536,
                # The maximum pixel threshold for the input image. If the image is larger, it is scaled down proportionally until its total pixels are below max_pixels.
                "max_pixels": 28 * 28 * 8192,
            },
            # If no built-in task is set for qwen-vl-ocr, you can pass a prompt in the text field. If no prompt is passed, the default prompt is used: Please output only the text content from the image without any additional descriptions or formatting.
            {
                "text": "ocr a json. Es un inventario de catálogo de autores, libros, datos , precios, y sumas Respeta el castellano y latín. mantén los datos de precios y números, también los de páginas"
            },
        ],
    }
]

response = dashscope.MultiModalConversation.call(
    # API keys for the Singapore and Beijing regions are different. To get an API key, see https://www.alibabacloud.com/help/en/model-studio/get-api-key
    # If you have not configured the environment variable, replace the following line with your Model Studio API key: api_key="sk-xxx"
    api_key=os.getenv("DASHSCOPE_API_KEY"),
    model="qwen3-vl-plus",
    messages=messages,
)
print(response)
print(response["output"]["choices"][0]["message"].content[0]["text"])