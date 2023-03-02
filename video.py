import os

from const import IMAGE_EXTENSIONS


def count_images(path: str) -> int:
    files = os.listdir(path)
    image_files = [file for file in files if '.' in file and file.split('.')[-1] in IMAGE_EXTENSIONS]
    return len(image_files)
