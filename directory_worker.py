import os

from const import IMAGE_EXTENSIONS


# TODO: Подобрать название поопрятнее
class DirectoryWorker:
    """
    Статический класс, отвечает за получение информации и взаимодействие с файлами и директориями ОС
    """
    @staticmethod
    def exists(path: str) -> bool:
        return os.path.exists(path)

    @staticmethod
    def get_filename(filename: str) -> str:
        """
        Извлекает имя файла без расширения
        :param filename: Имя файла
        :return: Непосредственное наименование файла
        """
        return ''.join(filename.split('.')[:-1])

    @staticmethod
    def get_extension(filename: str) -> str:
        """
        Извлекает расширение файла
        :param filename: Имя файла
        :return: Расширение файла
        """
        filename_parts = filename.split('.')
        return filename_parts[-1] if len(filename_parts) > 1 else ''

    @staticmethod
    def is_image(filename: str) -> bool:
        """
        Определяет, является ли файл изображением. Проверка происходит путем проверки расширения.
        :param filename: Файл
        :return: Изображение или нет
        """
        return DirectoryWorker.get_extension(filename).lower() in IMAGE_EXTENSIONS

    @staticmethod
    def get_images(path: str) -> list[str]:
        """
        Возвращает список изображений в директории
        :param path: Директория
        :return: Список изображений
        """
        return [file for file in os.listdir(path) if DirectoryWorker.is_image(file)]

    @staticmethod
    def count_images(path: str) -> int:
        """
        Подсчитывает количество изображений в дирекотрии.
        :param path: Путь до папки с изображениями
        :return: Количество изображений
        """
        return len(DirectoryWorker.get_images(path))

    @staticmethod
    def get_image_index(path: str) -> int:
        """
        Возвращает индекс последнего изображения в папке.
        :param path: Путь до папки с изображениями
        :return: Индекс либо 0, если в папке нет изображений
        """
        images = DirectoryWorker.get_images(path)
        numbers = [int(DirectoryWorker.get_filename(file)) for file in images]
        return max(numbers) + 1 if images else 0

    @staticmethod
    def delete_images(path: str):
        """
        Удаляет изображения в директории
        :param path: Директория
        :return:
        """
        for filename in DirectoryWorker.get_images(path):
            os.remove(f'{path}/{filename}')
