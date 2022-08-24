import os
import sys
import base64
from io import BytesIO

from django.core.files.uploadedfile import InMemoryUploadedFile
from PIL import Image, ImageFile
ImageFile.LOAD_TRUNCATED_IMAGES = True

from api.objects.constants import valid_images


def get_file_size(file):
    file.seek(0, os.SEEK_END)
    file_size = file.tell()

    file.seek(0)  # Get the cursor back to the first file bin

    return file_size


def convert_base64_to_jpg(img, img_name):
    img_data = Image.open(BytesIO(base64.b64decode(img)))
    img_data = img_data.convert("RGB")
    width, height = img_data.size

    temp_store = BytesIO()
    # Resize image
    compressed_width = 320
    compressed_heigth = int(height / width * compressed_width)
    compressed_size = (compressed_width, compressed_heigth)
    img_data = img_data.resize(compressed_size, Image.ANTIALIAS)

    img_data.save(temp_store, format="JPEG", optimize=True)

    file = InMemoryUploadedFile(
        temp_store,
        None,
        f"{img_name}.jpg",
        "image/jpeg",
        sys.getsizeof(temp_store),
        None,
    )

    return file


def get_img_dimension(file):
    img = Image.open(file)
    width, height = img.size

    return [width, height]


def get_valid_img_ext(filename):
    ext = filename.split('.')[-1]

    return ext if ext in valid_images else False


def get_file_extension(file_name):
    return file_name.split(".")[1]
