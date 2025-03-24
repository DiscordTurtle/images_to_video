import openai
import os
from PIL import Image
import base64
from io import BytesIO


with open ("openai_api_key.txt", "r") as file:
    openai.api_key = file.read()


def encode_image(image_path):
    """Encodes an image to a base64 string."""
    with open(image_path, "rb") as img_file:
        return base64.b64encode(img_file.read()).decode("utf-8")

def generate_sales_pitch(images, prompt):
    """Generates a salesperson-style speech for the given images and prompt."""
    encoded_images = [encode_image(img) for img in images]
    
    response = openai.ChatCompletion.create(
        model="gpt-4-vision-preview",  # Use GPT-4 with vision capabilities
        messages=[
            {"role": "system", "content": "You are a charismatic salesperson presenting these images."},
            {"role": "user", "content": prompt},
            {"role": "user", "content": [{"type": "image", "image": img} for img in encoded_images]}
        ],
        max_tokens=500
    )
    
    return response["choices"][0]["message"]["content"]

# Example Usage
image_paths = ["images/1.jpg", "images/2.jpg"]  # Replace with your images
prompt_text = "Imagine you are a salesmen, talking over these pictures, over a 10 second video. Try to sell this product to me."

sales_pitch = generate_sales_pitch(image_paths, prompt_text)
print(sales_pitch)
