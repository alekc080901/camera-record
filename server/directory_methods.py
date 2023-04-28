import os
import re

from pathlib import Path

from transliterate import translit

from server.const import IMAGE_EXTENSIONS

    
def exists(path: str) -> bool:
    """
    Есть ли файл/папка по пути
    :param path: Путь
    :return: True or False
    """
    return os.path.exists(path)


def get_filename(filename: str) -> str:
    """
    Извлекает имя файла без расширения
    :param filename: Имя файла
    :return: Непосредственное наименование файла
    """
    return ''.join(filename.split('.')[:-1])


def get_extension(filename: str) -> str:
    """
    Извлекает расширение файла
    :param filename: Имя файла
    :return: Расширение файла
    """
    filename_parts = filename.split('.')
    return filename_parts[-1] if len(filename_parts) > 1 else ''


def extract_filename(path: str):
    """
    Извлекает полное имя файла из пути.
    Пример: 'hello/world.txt' -> 'world.txt'.
    :param path: Путь к файлу (необязательно должен существовать)
    :return: Полное имя файла
    """
    return os.path.basename(path)


def is_image(filename: str) -> bool:
    """
    Определяет, является ли файл изображением. Проверка происходит путем проверки расширения.
    :param filename: Файл
    :return: Изображение или нет
    """
    return get_extension(filename).lower() in IMAGE_EXTENSIONS


def get_images(path: str) -> list[str]:
    """
    Возвращает список изображений в директории
    :param path: Директория
    :return: Список изображений
    """
    return [file for file in os.listdir(path) if is_image(file)]


def count_images(path: str) -> int:
    """
    Подсчитывает количество изображений в дирекотрии.
    :param path: Путь до папки с изображениями
    :return: Количество изображений
    """
    return len(get_images(path))


def get_next_image_index(path: str) -> int:
    """
    Возвращает индекс последнего изображения в папке.
    :param path: Путь до папки с изображениями
    :return: Индекс или 0, если в папке нет изображений
    """
    images = get_images(path)
    numbers = [int(get_filename(file)) for file in images]
    return max(numbers) + 1 if images else 0


def delete_images(path: str):
    """
    Удаляет изображения в директории
    :param path: Директория
    :return:
    """
    for filename in get_images(path):
        os.remove(f'{path}/{filename}')


def extract_directories(path: str):
    """
    Извлекает из пути все папки и подпапки в порядке от родителя к ребенку.
    Путь должен существовать.
    Пример: 'server/disk_uploader/disk_process.py' -> ['server', 'server/disk_uploader'].
    :param path: Путь до папки/файла
    :return: Список директорий
    """
    dirs = re.split(r'/|\\', path)
    dirs = dirs if Path(path).is_dir() else dirs[:-1]

    prev_dir = ''
    for i, d in enumerate(dirs):
        dirs[i] = os.path.join(prev_dir, d).replace('\\', '/')
        prev_dir = dirs[i]

    return dirs


def change_extension(path: str, extension: str, rename_file=False):
    """
    Меняет расширение файла, не трогая его имя.
    Пример: ('server/file.txt', 'mkv') -> 'server/file.mkv'.
    :param path: Путь до файла
    :param extension: Новое расширение
    :param rename_file: Нужно ли менять расширение у файла в ОС
    :return: Путь к файлу с новым расширением
    """
    if os.path.isdir(path):
        return

    new_path = f'{path[:path.rfind(".")]}.{extension}'

    if rename_file and not os.path.exists(new_path):
        os.rename(path, new_path)
    return new_path


def rename(old_path: str, new_path: str):
    """
    Переименовывание файла.
    :param old_path: Путь до файла
    :param new_path: Путь до файла с новым именем
    """
    os.replace(old_path, new_path)


def create_copy_of_filename(path: str) -> str:
    """
    Создает дубликат имени файла.
    Пример: 'hello/world.txt' ->  'hello/world_.txt'
    :param path: Путь к файлу (необязательно должен существовать)
    :return: Дубликат имени файла
    """
    filename = f'{get_filename(extract_filename(path))}_'
    extension = get_extension(path)
    directory = os.path.dirname(path)
    return os.path.join(directory, f'{filename}.{extension}').replace('\\', '/')


def to_directory_friendly(string: str) -> str:
    """
    Переводит русское название в английское и заменяет пробелы нижним подчеркиванием.
    :param string: Строка
    :return: Обработанная строка
    """
    string = string.replace(' ', '_')
    return translit(string, 'ru', reversed=True)


def mkdir(path: str):
    """
    Создает директории и поддиректории соответственно
    :param path: Путь с директориями
    """
    Path(path).mkdir(parents=True, exist_ok=True)
