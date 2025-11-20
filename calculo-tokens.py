import math
# To install the Pillow library, run the following command: pip install Pillow
from PIL import Image

def token_calculate(image_path):
    # Open the specified PNG image file.
#    image = Image.open("./pagina_0006.jpg")

    # Get the original dimensions of the image.
    height = 5538
    width = 8120
    
    # For models such as Qwen3-VL, and those updated after qwen-vl-max-0815, qwen-vl-max-0813, and qwen-vl-plus-0815, adjust the height and width to be multiples of 32.
    # For other models, adjust the height and width to be multiples of 28.
    h_bar = round(height / 32) * 32 
    w_bar = round(width / 32) * 32
    
    # Minimum tokens for an image: 4 tokens
    min_pixels = 32 * 32 * 4
    # Maximum tokens for an image: 1280 tokens
    max_pixels = 1280 * 32 * 32
        
    # Scale the image to ensure the total number of pixels is within the range of [min_pixels, max_pixels].
    if h_bar * w_bar > max_pixels:
        # Calculate the zoom factor beta so that the total number of pixels in the scaled image does not exceed max_pixels.
        beta = math.sqrt((height * width) / max_pixels)
        # Recalculate the adjusted height and width. For models such as Qwen3-VL and those updated after qwen-vl-max-0815 and qwen-vl-plus-0815, ensure the height and width are multiples of 32. For other models, ensure they are multiples of 28.
        h_bar = math.floor(height / beta / 32) * 32
        w_bar = math.floor(width / beta / 32) * 32
    elif h_bar * w_bar < min_pixels:
        # Calculate the zoom factor beta so that the total number of pixels in the scaled image is not less than min_pixels.
        beta = math.sqrt(min_pixels / (height * width))
        # Recalculate the adjusted height. For models such as Qwen3-VL and those updated after qwen-vl-max-0815 and qwen-vl-plus-0815, ensure it is a multiple of 32. For other models, ensure it is a multiple of 28.
        h_bar = math.ceil(height * beta / 32) * 32
        w_bar = math.ceil(width * beta / 32) * 32
    return h_bar, w_bar

# Replace test.png with the path to your local image.
h_bar, w_bar = token_calculate("test.png")
print(f"Scaled image dimensions: Height={h_bar}, Width={w_bar}")

# Calculate the number of tokens for the image. For models such as Qwen3-VL and those updated after qwen-vl-max-0815 and qwen-vl-plus-0815, the number of tokens = total pixels / (32 * 32). For other models, the number of tokens = total pixels / (28 * 28).
token = int((h_bar * w_bar) / (32 * 32))

# The system automatically adds the <|vision_bos|> and <|vision_eos|> visual markers (1 token each).
print(f"Number of tokens for the image: {token + 2}")
